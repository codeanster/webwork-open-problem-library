from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "data"


@pytest.fixture
def classic_pg() -> str:
    return (FIXTURES_DIR / "simple_classic.pg").read_text(encoding="utf-8")


@pytest.fixture
def pgml_pg() -> str:
    return (FIXTURES_DIR / "sample_pgml.pg").read_text(encoding="utf-8")

