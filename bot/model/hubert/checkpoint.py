"""Utility functions for converting and loading pretrained checkpoints."""

import argparse
import json
import logging
from pathlib import Path
from typing import Literal

import ml.api as ml
import safetensors.torch as st
import torch
from huggingface_hub import hf_hub_download
from omegaconf import OmegaConf
from safetensors import safe_open
from torch import Tensor

from bot.model.hubert.model import HubertModel

logger = logging.getLogger(__name__)

PretrainedHubertModel = Literal["lucy"]

REPO_ID = "codekansas/dpshai"


def _load_model(key: str, ckpt_path: str | Path | None = None) -> HubertModel:
    if ckpt_path is None:
        ckpt_path = hf_hub_download(REPO_ID, key)
    ckpt = st.load_file(ckpt_path)
    with safe_open(ckpt_path, framework="pt", device="cpu") as f:
        metadata = f.metadata()
        config = json.loads(metadata["config"])
    model = HubertModel(name=key, **config)
    model.load_state_dict(ckpt)
    model.requires_grad_(False)
    return model


def pretrained_hubert(key: PretrainedHubertModel) -> HubertModel:
    match key:
        case "lucy":
            return _load_model("lucy.bin")

        case _:
            raise NotImplementedError(f"Unknown pretrained HuBERT key: {key}")


def convert_script() -> None:
    ml.configure_logging()

    parser = argparse.ArgumentParser(description="Converts a HuBERT checkpoint to a safetensors file")
    parser.add_argument("ckpt_path", type=str, help="Path to the checkpoint file")
    parser.add_argument("-o", "--output", type=str, help="Output file name", default="hubert.bin")
    args = parser.parse_args()
    ckpt_path = args.ckpt_path
    full_ckpt = torch.load(ckpt_path, map_location="cpu")
    config_str = full_ckpt["config"]
    config = OmegaConf.create(config_str).model
    model = HubertModel(
        name="exporting",
        num_timesteps=config.num_timesteps,
        num_layers=config.num_layers,
        embedding_dims=config.embedding_dims,
        contraction_factor=config.contraction_factor,
        autoencoder_type=config.autoencoder_type,
        speech_representation_type=config.speech_representation_type,
    )
    ckpt: dict[str, Tensor] = full_ckpt["model"]
    model.load_state_dict(ckpt)
    metadata = {
        "config": json.dumps(
            {
                "num_timesteps": config.num_timesteps,
                "num_layers": config.num_layers,
                "embedding_dims": config.embedding_dims,
                "contraction_factor": config.contraction_factor,
                "autoencoder_type": config.autoencoder_type,
                "speech_representation_type": config.speech_representation_type,
            }
        )
    }
    st.save_file(ckpt, args.output, metadata)
    logger.info("Done.")


if __name__ == "__main__":
    # python -m bot.model.hubert.checkpoint
    convert_script()
