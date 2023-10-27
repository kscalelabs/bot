"""Script for extracting the model weights from a trained checkpoint."""

import logging

import torch
import torch.nn.functional as F
from ml.models.architectures.attention import TransformerEncoder, TransformerEncoderLayer
from ml.tasks.diffusion import GaussianDiffusion, get_diffusion_beta_schedule
from pretrained.hubert import PretrainedHubertKmeansSize, PretrainedHubertSize
from torch import Tensor, nn

from bot.model.modules.autoencoder import AutoencoderType, get_autoencoder
from bot.model.modules.hubert_soft import PretrainedHubertSoftSize
from bot.model.modules.speech_representations import SpeechRepresentationType, get_speech_representation

logger = logging.getLogger(__name__)

HUBERT_SAMPLE_RATE = 16000


class SpeakerEncoderModel(nn.Module):
    def __init__(
        self,
        autoencoder_dims: int,
        embedding_dims: int,
        num_layers: int,
        contraction_fact: int,
    ) -> None:
        """Instantiates the encoder model.

        Args:
            autoencoder_dims: Number of autoencoder hidden dimensions.
            num_codes: Size of the output embeddings.
            embedding_dims: Transformer embedding dimension.
            num_layers: Number of transformer layers.
            contraction_fact: Contraction factor for the time dimension.
        """
        super().__init__()

        self.autoencoder_proj_in = nn.Conv1d(
            autoencoder_dims,
            embedding_dims,
            kernel_size=contraction_fact,
            stride=contraction_fact,
        )
        self.cls_tok = nn.Parameter(torch.randn(1, 1, embedding_dims))

        # Transformer model.
        self.transformer = TransformerEncoder(
            TransformerEncoderLayer(
                d_model=embedding_dims,
                nhead=embedding_dims // 64,
                dim_feedforward=embedding_dims * 4,
                dropout=0.1,
            ),
            num_layers=num_layers,
            use_rotary=True,
            is_causal=False,
        )

    def forward(self, latents: Tensor) -> Tensor:
        x = self.autoencoder_proj_in(latents.transpose(1, 2)).transpose(1, 2)
        x = torch.cat([x, self.cls_tok.repeat(x.shape[0], 1, 1)], dim=1)
        x, _ = self.transformer(x)
        return x[:, -1]


class DiffusionTransformer(nn.Module):
    def __init__(
        self,
        hubert_dims: int,
        autoencoder_dims: int,
        num_timesteps: int,
        embedding_dims: int,
        num_layers: int,
        contraction_fact: int,
    ) -> None:
        """Instantiates the diffusion model.

        Args:
            hubert_dims: Number of HuBERT hidden dimensions.
            autoencoder_dims: Number of autoencoder hidden dimensions.
            num_timesteps: Number of diffusion timesteps.
            embedding_dims: Transformer embedding dimension.
            num_layers: Number of transformer layers.
            contraction_fact: Contraction factor for the time dimension.
        """
        super().__init__()

        # Projects HuBERT embeddings to latent space.
        self.hubert_proj = nn.Conv1d(hubert_dims, embedding_dims, contraction_fact, contraction_fact)

        # Project the latent input to the transformer space.
        self.auto_proj_in = nn.Conv1d(autoencoder_dims, embedding_dims, contraction_fact, contraction_fact)
        self.auto_proj_out = nn.ConvTranspose1d(embedding_dims, autoencoder_dims, contraction_fact, contraction_fact)

        # Embeddings for the speaker, time and HuBERT codes.
        self.time_emb = nn.Embedding(num_timesteps, embedding_dims)

        # Transformer model.
        self.transformer = TransformerEncoder(
            TransformerEncoderLayer(
                d_model=embedding_dims,
                nhead=embedding_dims // 64,
                dim_feedforward=embedding_dims * 4,
                dropout=0.1,
            ),
            num_layers=num_layers,
            use_rotary=True,
            is_causal=False,
        )

    def forward(self, latents: Tensor, hubert_embs: Tensor, times: Tensor, speaker_emb: Tensor) -> Tensor:
        assert latents.dim() == 3
        assert hubert_embs.dim() == 3
        assert times.dim() == 1
        assert speaker_emb.dim() == 2

        x = (
            self.auto_proj_in(latents.transpose(1, 2)).transpose(1, 2)
            + self.hubert_proj(hubert_embs.transpose(1, 2)).transpose(1, 2)
            + self.time_emb(times).unsqueeze(1)
            + speaker_emb.unsqueeze(1)
        )

        x, _ = self.transformer(x)
        x = self.auto_proj_out(x.transpose(1, 2)).transpose(1, 2)

        return x


class HubertModel(nn.Module):
    __constants__ = ["name", "sample_rate", "stride_factor", "contraction_factor"]

    def __init__(
        self,
        name: str,
        num_timesteps: int = 500,
        num_layers: int = 8,
        embedding_dims: int = 1024,
        contraction_factor: int = 2,
        autoencoder_type: AutoencoderType = "hifigan",
        speech_representation_type: SpeechRepresentationType = "hubert-quantized",
        *,
        hubert_size: PretrainedHubertSize = "base",
        hubert_output_layer: int | float = 0.8,
        hubert_quantized_size: PretrainedHubertKmeansSize = "base-l10-c100",
        hubert_soft_size: PretrainedHubertSoftSize = "base",
    ) -> None:
        super().__init__()

        self.name = name
        self.sample_rate = 16_000

        # Pre-trained HuBERT model.
        self.hubert = get_speech_representation(
            speech_representation_type,
            hubert_size=hubert_size,
            hubert_output_layer=hubert_output_layer,
            hubert_quantized_size=hubert_quantized_size,
            hubert_soft_size=hubert_soft_size,
        )

        # Autoencoder model.
        self.autoencoder = get_autoencoder(autoencoder_type, HUBERT_SAMPLE_RATE)
        self.stride_factor = 320 / self.autoencoder.stride
        self.contraction_factor = contraction_factor

        # Speaker embedding model.
        self.speaker_emb = SpeakerEncoderModel(
            autoencoder_dims=self.autoencoder.autoencoder_dims,
            embedding_dims=embedding_dims,
            num_layers=num_layers,
            contraction_fact=contraction_factor,
        )

        # Diffusion model.
        self.diff = GaussianDiffusion(
            betas=get_diffusion_beta_schedule("cosine", num_timesteps),
            pred_mode="pred_x_0",
            loss="mse",
            sigma_type="upper_bound",
        )

        # Diffusion model, conditioned on HuBERT embeddings, speaker ID and time.
        self.model = DiffusionTransformer(
            hubert_dims=self.hubert.dimensions,
            autoencoder_dims=self.autoencoder.autoencoder_dims,
            num_timesteps=num_timesteps,
            embedding_dims=embedding_dims,
            num_layers=num_layers,
            contraction_fact=contraction_factor,
        )

    @torch.no_grad()
    def get_audio_latents(self, audio: Tensor) -> tuple[Tensor, Tensor]:
        if audio.dim() == 3:
            audio = audio.squeeze(1)
        audio = audio.squeeze(1)

        # Latent space of the autoencoder, cropped by the contraction factor.
        latents = self.autoencoder.encode(audio)
        cf = self.contraction_factor
        l_tsz = latents.shape[1]
        diff = l_tsz % cf
        if diff != 0:
            start, end = diff // 2, l_tsz - (diff + 1) // 2
            latents = latents[:, start:end]

        return audio, latents

    def get_inputs(self, audio: Tensor, ref_audio: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        """Gets the latent vectors and HuBERT embeddings for the given audio.

        Args:
            audio: The input audio, with shape ``(B, T)``
            ref_audio: The reference audio, with shape ``(B, T)``

        Returns:
            The latent vector and HuBERT embeddings, with shapes ``(B, T', Dl)``
            and ``(B, T;, Dh)``, respectively, where ``T'`` is the number of
            timesteps, ``Dl`` is the number of autoencoder dimensions, and
            ``Dh`` is the number of HuBERT dimensions.
        """
        audio, latents = self.get_audio_latents(audio)
        ref_audio, ref_latents = self.get_audio_latents(ref_audio)
        l_tsz = latents.shape[1]

        # Gets the HuBERT embeddings, cropped to match the latent space.
        hubert_embeddings = self.hubert(audio, sample_rate=HUBERT_SAMPLE_RATE)
        h_tsz = hubert_embeddings.shape[1]

        # Stretches the HuBERT embeddings to match the latent space stride.
        if self.stride_factor != 1:
            # inds = torch.linspace(0, h_tsz - 1, round(h_tsz * self.stride_factor), device=hubert_embeddings.device)
            # hubert_embeddings = hubert_embeddings[:, inds.round().long()]
            hubert_embeddings = F.interpolate(
                hubert_embeddings.transpose(1, 2),
                scale_factor=self.stride_factor,
                mode="linear",
                align_corners=True,
            )
            hubert_embeddings = hubert_embeddings.transpose(1, 2)
            h_tsz = hubert_embeddings.shape[1]

        # Clips any extra part of the latent space or HuBERT embeddings.
        diff = l_tsz - h_tsz
        if diff > 0:
            latents = latents[:, diff // 2 : l_tsz - ((diff + 1) // 2)]
        elif diff < 0:
            hubert_embeddings = hubert_embeddings[:, -diff // 2 : h_tsz - ((-diff + 1) // 2)]
        assert latents.shape[:2] == hubert_embeddings.shape[:2]

        return latents, ref_latents, hubert_embeddings

    @torch.no_grad()
    def get_audio(self, latents: Tensor) -> Tensor:
        return self.autoencoder.decode(latents)

    def forward(self, audio: Tensor, ref_audio: Tensor) -> Tensor:
        latents, ref_latents, hubert_embeddings = self.get_inputs(audio, ref_audio)
        cond_emb = self.speaker_emb(ref_latents)
        loss = self.diff.loss(lambda x, times: self.model(x, hubert_embeddings, times, cond_emb), latents)
        return loss

    def infer(self, audio: Tensor, ref_audio: Tensor, sampling_timesteps: int | None = None) -> tuple[Tensor, Tensor]:
        latents, ref_latents, hubert_embeddings = self.get_inputs(audio, ref_audio)
        cond_emb = self.speaker_emb(ref_latents)
        shape, device = latents.shape, latents.device
        sample = self.diff.sample(
            lambda x, times: self.model(x, hubert_embeddings, times, cond_emb),
            shape,
            device,
            sampling_timesteps,
        )
        return sample, latents

    @torch.no_grad()
    def run(self, audio: Tensor, ref_audio: Tensor, sampling_timesteps: int | None = None) -> Tensor:
        assert audio.dim() == 2, f"Expected 2D audio, got {audio.shape}"
        assert ref_audio.dim() == 2, f"Expected 2D reference audio, got {ref_audio.shape}"
        assert audio.shape[0] == ref_audio.shape[0], f"Batch size mismatch for {audio.shape=} != {ref_audio.shape=}"
        sample, _ = self.infer(audio, ref_audio, sampling_timesteps)
        return self.get_audio(sample[1]).squeeze(1)
