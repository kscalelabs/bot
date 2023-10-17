"""Utility functions for converting and loading pretrained checkpoints."""

import argparse
import json
import logging

import safetensors.torch as st
import torch
from ml.utils.logging import configure_logging
from omegaconf import OmegaConf
from torch import Tensor

from bot.model.hubert.model import HubertModel

logger = logging.getLogger(__name__)


def convert_script() -> None:
    configure_logging()

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
    config = {
        "num_timesteps": config.num_timesteps,
        "num_layers": config.num_layers,
        "embedding_dims": config.embedding_dims,
        "contraction_factor": config.contraction_factor,
        "autoencoder_type": config.autoencoder_type,
        "speech_representation_type": config.speech_representation_type,
    }
    metadata = {"config": json.dumps(config)}
    st.save_file(ckpt, args.output, metadata)
    logger.info("Done.")


if __name__ == "__main__":
    # python -m bot.model.hubert.checkpoint
    convert_script()
