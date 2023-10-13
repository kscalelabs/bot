"""Supports autoencoder models for speech compression.

These modules are for INFERENCE ONLY and expect the checkpoint to contain the
weights for each of the modules, and don't load any pretrained weights here.
"""

from abc import ABC, abstractmethod
from typing import Literal, cast, get_args

import torch
from pretrained.vocoder.hifigan import PretrainedHiFiGANType, pretrained_hifigan
from torch import Tensor, nn

AutoencoderType = Literal["hifigan"]


def cast_autoencoder_type(s: str) -> AutoencoderType:
    assert s in get_args(AutoencoderType), f"Invalid autoencoder type: {s}"
    return cast(AutoencoderType, s)


class BaseAutoencoder(nn.Module, ABC):
    @property
    @abstractmethod
    def stride(self) -> int:
        """Returns the stride of the autoencoder.

        Returns:
            The autoencoder stride.
        """

    @property
    @abstractmethod
    def autoencoder_dims(self) -> int:
        """Returns the number of autoencoder dimensions.

        Returns:
            Number of autoencoder dimensions.
        """

    @torch.no_grad()
    @abstractmethod
    def encode(self, audio: Tensor) -> Tensor:
        """Encodes audio to latent features.

        Args:
            audio: The audio tensor to encode, with shape ``(B, T)``

        Returns:
            The latent features, with shape ``(B, T', D)``, where ``T'`` is the
            number of timesteps and ``D`` is the number of autoencoder
            dimensions.
        """

    @torch.no_grad()
    @abstractmethod
    def decode(self, latents: Tensor) -> Tensor:
        """Decodes latent features to audio.

        Args:
            latents: The latent features, with shape ``(B, T', D)``.

        Returns:
            The audio tensor, with shape ``(B, T)``.
        """


class Normalizer(nn.Module):
    def __init__(self, dims: int) -> None:
        super().__init__()

        self.register_buffer("loc", torch.zeros(dims))
        self.register_buffer("scale", torch.ones(dims))
        self.register_buffer("ema", torch.zeros(1))

    loc: Tensor
    scale: Tensor
    ema: Tensor

    def normalize(self, x: Tensor) -> Tensor:
        """Normalizes a signal along the final dimension.

        This updates the running mean and standard deviation of the signal
        if training.

        Args:
            x: The input tensor, with shape ``(*, N)``

        Returns:
            The normalized tensor, with shape ``(*, N)``
        """
        if self.training:
            mean, std = x.flatten(0, 1).mean(0), x.flatten(0, 1).std(0)
            self.loc.mul_(self.ema).add_(mean * (1 - self.ema))
            self.scale.mul_(self.ema).add_(std * (1 - self.ema))
            self.ema.add_(0.001 * (1 - self.ema))
        x = (x - self.loc) / self.scale
        return x

    def denormalize(self, x: Tensor) -> Tensor:
        """Denormalizes a signal along the final dimension.

        Args:
            x: The latent tensor, with shape ``(*, N)``

        Returns:
            The denormalized tensor, with shape ``(*, N)``
        """
        return x * self.scale + self.loc


class HifiganAutoencoder(BaseAutoencoder):
    def __init__(self, key: PretrainedHiFiGANType) -> None:
        super().__init__()

        # Pre-trained autoencoder model.
        hifigan = pretrained_hifigan(key, pretrained=False)
        self.hifigan = hifigan
        self.audio_to_mels = hifigan.audio_to_mels()
        self._autoencoder_dims = hifigan.model_in_dim
        self.normalizer = Normalizer(self.autoencoder_dims)

    @property
    def stride(self) -> int:
        return self.hifigan.hop_size

    @property
    def autoencoder_dims(self) -> int:
        return self._autoencoder_dims

    @torch.no_grad()
    def encode(self, audio: Tensor) -> Tensor:
        assert audio.dim() == 2
        x = self.audio_to_mels(audio).transpose(1, 2)
        x = self.normalizer.normalize(x)
        return x

    @torch.no_grad()
    def decode(self, latents: Tensor) -> Tensor:
        x = self.normalizer.denormalize(latents)
        x = x.transpose(1, 2)
        x = self.hifigan.infer(x)
        x = x.squeeze(1)
        return x


def get_autoencoder(autoencoder_type: AutoencoderType, sample_rate: int) -> BaseAutoencoder:
    match autoencoder_type:
        case "hifigan":
            match sample_rate:
                case 16000:
                    return HifiganAutoencoder("16000hz")
                case 22050:
                    return HifiganAutoencoder("22050hz")
                case _:
                    raise NotImplementedError(f"Unsupported sample rate for HiFiGAN: {sample_rate}")
        case _:
            raise ValueError(f"Invalid autoencoder type: {autoencoder_type}")
