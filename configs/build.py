"""Script to build a single configuration file from a template."""

import argparse
from pathlib import Path

from omegaconf import OmegaConf

from bot.settings import Settings, _load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a configuration file from a template.")
    parser.add_argument("key", choices=["local", "aws"], help="Configuration key")
    parser.add_argument("-o", "--output-file", help="Output file path")
    args = parser.parse_args()

    # Gets the path to the configuration files.
    base_dir = Path(__file__).parent.resolve()
    shared_dir, conf_dir = base_dir / "shared", base_dir / args.key
    if not shared_dir.exists() or not conf_dir.exists():
        raise ValueError(f"Directory not found: {shared_dir} / {conf_dir}")

    # Loads the configuration files.
    raw_configs = (OmegaConf.load(config) for d in (conf_dir, shared_dir) for config in d.glob("*.yaml"))
    config = OmegaConf.merge(OmegaConf.structured(Settings), *raw_configs)
    OmegaConf.resolve(config)

    if args.output_file is None:
        config_string = OmegaConf.to_yaml(config)
        _load_settings(OmegaConf.create(config_string))
        print(config_string)
    else:
        output_file = Path(args.output_file).expanduser().resolve()
        output_file.parent.mkdir(exist_ok=True, parents=True)
        with open(output_file, "w") as f:
            OmegaConf.save(config, f)
        _load_settings(OmegaConf.load(output_file))


if __name__ == "__main__":
    main()
