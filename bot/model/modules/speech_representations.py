"""Supports various types of speech representations.

All of these modules are meant to be used for INFERENCE ONLY. In other words,
we expect the checkpoint to contain the weights for each of the modules, and
don't load any pretrained weights here.
"""

from abc import ABC, abstractmethod
from typing import Literal, cast, get_args

from pretrained.hubert import (
    PretrainedHubertKmeansSize,
    PretrainedHubertSize,
    pretrained_hubert,
    pretrained_hubert_with_kmeans,
)
from torch import Tensor, nn

from bot.model.modules.hubert_soft import PretrainedHubertSoftSize, pretrained_hubert_soft

SpeechRepresentationType = Literal["hubert", "hubert-quantized", "hubert-soft"]


def cast_speech_representation_type(s: str) -> SpeechRepresentationType:
    assert s in get_args(SpeechRepresentationType), f"Invalid speech representation type: {s}"
    return cast(SpeechRepresentationType, s)


class BaseSpeechRepresentation(nn.Module, ABC):
    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Returns the number of dimensions of the speech representation.

        Returns:
            The number of dimensions of the speech representation.
        """

    @abstractmethod
    def forward(self, audio: Tensor, sample_rate: int) -> Tensor:
        """Encodes the audio into the speech representation.

        Args:
            audio: The input audio, with shape ``(B, T)``.
            sample_rate: The audio sample rate.

        Returns:
            The audio representation, with shape ``(B, T', dimensions)``.
        """


class HubertSpeechRepresentation(BaseSpeechRepresentation):
    def __init__(
        self,
        size: PretrainedHubertSize = "base",
        output_layer: int | float = 0.8,
    ) -> None:
        super().__init__()

        self.hubert = pretrained_hubert(size, load_weights=False)
        self.hubert.set_output_layer(output_layer)

    @property
    def dimensions(self) -> int:
        return self.hubert.hidden_size

    def forward(self, audio: Tensor, sample_rate: int) -> Tensor:
        return self.hubert(audio, sample_rate)


class HubertQuantizedSpeechRepresentation(BaseSpeechRepresentation):
    """Uses the quantized latent dimension of the HuBERT model."""

    def __init__(self, size: PretrainedHubertKmeansSize = "base-l10-c100") -> None:
        super().__init__()

        self.hubert, self.kmeans = pretrained_hubert_with_kmeans(size, load_weights=False)
        self.embeddings = nn.Embedding(self.kmeans.n_clusters, self.hubert.hidden_size)

    @property
    def dimensions(self) -> int:
        return self.hubert.hidden_size

    def forward(self, audio: Tensor, sample_rate: int) -> Tensor:
        x = self.hubert(audio, sample_rate)
        x = self.kmeans(x)
        x = self.embeddings(x)
        return x


class HubertSoftSpeechRepresentation(BaseSpeechRepresentation):
    """Pre-trained model which predicts the HuBERT embedding."""

    def __init__(self, size: PretrainedHubertSoftSize) -> None:
        super().__init__()

        self.hubert = pretrained_hubert_soft(size)
        self.proj = nn.Linear(self.hubert.num_codes, self.hubert.hubert.hidden_size)

    @property
    def dimensions(self) -> int:
        return self.hubert.hubert.hidden_size

    def forward(self, audio: Tensor, sample_rate: int) -> Tensor:
        return self.proj(self.hubert(audio, sample_rate, True))


def get_speech_representation(speech_representation_type: SpeechRepresentationType) -> BaseSpeechRepresentation:
    match speech_representation_type:
        case "hubert":
            return HubertSpeechRepresentation()
        case "hubert-quantized":
            return HubertQuantizedSpeechRepresentation()
        case "hubert-soft":
            return HubertSoftSpeechRepresentation("base")
        case _:
            raise ValueError(f"Invalid speech representation type: {speech_representation_type}")
