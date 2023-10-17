"""Utility functions for loading pretrained models."""

import json
from pathlib import Path
from typing import Literal, cast, get_args

import safetensors.torch as st
from huggingface_hub import hf_hub_download
from safetensors import safe_open

from bot.model.hubert.model import HubertModel
from bot.settings import load_settings

PretrainedHubertModel = Literal["hubert-quantized-20231015"]

REPO_ID = "codekansas/dpshai"


def cast_pretrained_model(key: str) -> PretrainedHubertModel:
    assert key in get_args(PretrainedHubertModel), f"Invalid pretrained HuBERT model: {key}"
    return cast(PretrainedHubertModel, key)


def _load_model(key: PretrainedHubertModel, ckpt_path: str | Path | None = None) -> HubertModel:
    settings = load_settings().model
    cache_dir_str, token = settings.cache_dir, settings.hf_hub_token
    cache_dir = None if cache_dir_str is None else Path(cache_dir_str).expanduser().resolve()
    if ckpt_path is None:
        ckpt_path = hf_hub_download(REPO_ID, f"{key}.bin", cache_dir=cache_dir, token=token)
    ckpt = st.load_file(ckpt_path)
    with safe_open(ckpt_path, framework="pt", device="cpu") as f:
        metadata = f.metadata()
        config = json.loads(metadata["config"])
    model = HubertModel(name=key, **config)
    model.load_state_dict(ckpt)
    model.requires_grad_(False)
    return model


def pretrained_hubert(key: PretrainedHubertModel) -> HubertModel:
    return _load_model(key)