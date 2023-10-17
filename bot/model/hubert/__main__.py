"""Run inference on a pair of audio files."""

import argparse
from typing import get_args

import soundfile as sf
import torch
import torchaudio.functional as A
from ml.utils.device.auto import detect_device

from bot.model.hubert.checkpoint import PretrainedHubertModel, pretrained_hubert


def main() -> None:
    parser = argparse.ArgumentParser(description="Run inference on a pair of audio files.")
    parser.add_argument("key", choices=get_args(PretrainedHubertModel), help="The pretrained model key")
    parser.add_argument("source", type=str, help="Path to the source audio file")
    parser.add_argument("reference", type=str, help="Path to the reference audio file")
    parser.add_argument("-o", "--output-file", type=str, default="output.flac", help="Path to the output audio file")
    args = parser.parse_args()

    device = detect_device()

    # Loads the pretrained model.
    model = pretrained_hubert(args.key)
    device.module_to(model)

    # Loads the source sample.
    source_arr, source_sr = sf.read(args.source)
    source = device.tensor_to(source_arr)
    if source.dim() == 2:
        source = source[..., 0]
    assert source.dim() == 1
    source = A.resample(source, source_sr, model.sample_rate)

    # Loads the reference sample.
    reference_arr, reference_sr = sf.read(args.reference)
    reference = device.tensor_to(reference_arr)
    if reference.dim() == 2:
        reference = reference[..., 0]
    assert reference.dim() == 1
    reference = A.resample(reference, reference_sr, model.sample_rate)

    # Runs inference.
    with device.autocast_context(), torch.no_grad():
        output = model.run(source.unsqueeze(0), reference.unsqueeze(0)).squeeze(0)

    # Saves the output.
    sf.write(args.output_file, output.float().cpu().numpy(), model.sample_rate)


if __name__ == "__main__":
    # python -m bot.model.hubert
    main()
