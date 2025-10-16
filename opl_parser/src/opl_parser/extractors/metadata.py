"""Utilities for parsing OPL metadata headers."""
from __future__ import annotations

from typing import Dict, Iterable, Tuple
import re

HEADER_PREFIX = "##"
HEADER_PATTERN = re.compile(r"^##\s*([A-Za-z0-9_]+)\((.*?)\)\s*$")


def _iter_header_lines(content: str) -> Iterable[str]:
    """Yield leading metadata comment lines until the first non-header line."""
    for line in content.splitlines():
        if line.strip().startswith(HEADER_PREFIX):
            yield line
        elif line.strip() == "":
            # allow blank lines between header entries
            continue
        else:
            break


def _normalize_key(raw_key: str) -> str:
    return raw_key.strip().lower()


def parse_metadata(content: str) -> Dict[str, str]:
    """Parse the standard `## KEY(value)` metadata block at the top of PG files."""
    metadata: Dict[str, str] = {}
    for line in _iter_header_lines(content):
        match = HEADER_PATTERN.match(line.strip())
        if not match:
            continue
        key, value = match.groups()
        metadata[_normalize_key(key)] = value.strip()
    return metadata


def parse_load_macros(content: str) -> Tuple[str, ...]:
    """Return macros referenced via loadMacros statements."""
    pattern = re.compile(r"loadMacros\((.*?)\);", re.DOTALL)
    macros = []
    for match in pattern.finditer(content):
        args = match.group(1)
        for raw in re.split(r",", args):
            cleaned = raw.strip().strip('"\'')
            if cleaned:
                macros.append(cleaned)
    return tuple(dict.fromkeys(macros))

