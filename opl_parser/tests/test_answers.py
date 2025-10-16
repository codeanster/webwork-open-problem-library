from __future__ import annotations

from opl_parser.extractors.answers import parse_answers


def test_parse_answers_numeric(classic_pg: str) -> None:
    summary = parse_answers(classic_pg)
    assert len(summary.answers) == 1
    assert summary.answers[0].type == "numeric"


def test_parse_answers_formula(pgml_pg: str) -> None:
    summary = parse_answers(pgml_pg)
    assert summary.answers[0].type == "formula"
