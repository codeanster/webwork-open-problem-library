from __future__ import annotations

from opl_parser.extractors.metadata import parse_metadata, parse_load_macros


def test_parse_metadata_extracts_headers(classic_pg: str) -> None:
    metadata = parse_metadata(classic_pg)
    assert metadata["dbsubject"] == "Algebra"
    assert metadata["dbchapter"] == "Quadratic equations"
    assert metadata["dbsection"] == "Concept"


def test_parse_load_macros_detects_unique_macros(classic_pg: str, pgml_pg: str) -> None:
    macros = parse_load_macros(classic_pg)
    assert "PG.pl" in macros
    pgml_macros = parse_load_macros(pgml_pg)
    assert "PGML.pl" in pgml_macros
