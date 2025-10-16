"""Command-line interface for the OPL parser."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
import yaml

from .parser import PGProblemParser, ParserConfig
from .serializers import JSONLWriter

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "parser.yaml"


def _load_config(path: Optional[Path]) -> dict:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@click.group()
def main() -> None:
    """Entry point for parser commands."""


@main.command("parse")
@click.option("--root", type=click.Path(path_type=Path), help="Root directory containing PG files")
@click.option("--output", "output_dir", type=click.Path(path_type=Path), help="Directory for JSONL output")
@click.option("--config", "config_path", type=click.Path(path_type=Path), help="Override config file path")
@click.option("--shard-size", type=int, help="Number of records per JSONL shard")
def parse_command(root: Optional[Path], output_dir: Optional[Path], config_path: Optional[Path], shard_size: Optional[int]) -> None:
    """Parse PG files and emit JSONL output."""
    base_config = _load_config(config_path)

    filters_cfg = base_config.get("filters", {})
    output_cfg = base_config.get("output", {})

    effective_root = root or Path(base_config.get("root", "."))
    effective_output = output_dir or Path(output_cfg.get("samples", "outputs/samples"))
    effective_shard = shard_size or output_cfg.get("shard_size", 1000)

    parser_config = ParserConfig(
        root=effective_root,
        include_extensions=tuple(filters_cfg.get("include_extensions", [".pg"])),
        exclude_directories=tuple(filters_cfg.get("exclude_directories", [])),
    )

    parser = PGProblemParser(config=parser_config)

    with JSONLWriter(Path(effective_output), shard_size=effective_shard) as writer:
        for record in parser.iter_directory():
            writer.write(record.dict())

    click.echo(f"Parsed PG files from {effective_root} into {effective_output}")


if __name__ == "__main__":
    main()
