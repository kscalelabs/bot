"""HuBERT soft model, for loading pretrained weights."""

from typing import Literal, cast, get_args

import torch.nn.functional as F
from pretrained.hubert import PretrainedHubertSize, pretrained_hubert
from torch import Tensor, nn

PretrainedHubertSoftSize = Literal["base"]


class HubertSoftModel(nn.Module):
    def __init__(
        self,
        hubert_key: PretrainedHubertSize,
        output_layer: int,
        num_codes: int,
    ) -> None:
        super().__init__()

        self.hubert_key = hubert_key
        self.output_layer = output_layer
        self.num_codes = num_codes

        # Loads pre-trained HuBERT model.
        hubert = pretrained_hubert(hubert_key, load_weights=False)
        hubert.set_output_layer(output_layer)
        self.hubert = hubert

        # Projects to code logits.
        self.proj = nn.Linear(hubert.hidden_size, num_codes)

    def forward(self, audio: Tensor, sample_rate: int, return_probs: bool = False) -> Tensor:
        x = self.hubert(audio, sample_rate)
        x = self.proj(x)
        if return_probs:
            x = F.softmax(x, dim=-1)
        return x


def cast_pretrained_hubert_soft_key(s: str) -> PretrainedHubertSoftSize:
    assert s in get_args(PretrainedHubertSoftSize), f"Invalid pretrained HuBERT key: {s}"
    return cast(PretrainedHubertSoftSize, s)


def pretrained_hubert_soft(key: PretrainedHubertSoftSize) -> HubertSoftModel:
    match key:
        case "base":
            return HubertSoftModel(
                hubert_key="base",
                output_layer=10,
                num_codes=100,
            )

        case _:
            raise NotImplementedError(f"Unknown pretrained HuBERT key: {key}")
