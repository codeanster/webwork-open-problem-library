"""Streaming JSONL serializers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Optional


class JSONLWriter:
    """Write problem records to sharded JSONL files."""

    def __init__(self, output_dir: Path, shard_size: int = 1000, prefix: str = "opl_problems") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.shard_size = shard_size
        self.prefix = prefix
        self._file_handle: Optional[object] = None
        self._shard_index = 0
        self._records_in_shard = 0

    def _open_next_shard(self) -> None:
        if self._file_handle:
            self._file_handle.close()
        filename = f"{self.prefix}-{self._shard_index:04d}.jsonl"
        self._file_handle = (self.output_dir / filename).open("w", encoding="utf-8")
        self._records_in_shard = 0
        self._shard_index += 1

    def write(self, record: Mapping[str, object]) -> None:
        if self._file_handle is None or self._records_in_shard >= self.shard_size:
            self._open_next_shard()
        assert self._file_handle is not None
        json_record = json.dumps(record, ensure_ascii=False)
        self._file_handle.write(json_record + "\n")
        self._records_in_shard += 1

    def write_many(self, records: Iterable[Mapping[str, object]]) -> None:
        for record in records:
            self.write(record)

    def close(self) -> None:
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def __enter__(self) -> "JSONLWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

