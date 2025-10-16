"""Convenience script for running the parser with config defaults."""
from __future__ import annotations

from opl_parser.cli import main


def run() -> None:
    """Invoke the CLI parser command."""
    main(standalone_mode=False)


if __name__ == "__main__":
    run()
