from __future__ import annotations

from opl_parser.extractors.text import parse_problem_text


def test_parse_problem_text_classic(classic_pg: str) -> None:
    parsed = parse_problem_text(classic_pg)
    assert parsed.student == ["Find the circumference of a circle with radius {radius}.\nAnswer: [INPUT]"]
    assert parsed.solutions == []


def test_parse_problem_text_pgml(pgml_pg: str) -> None:
    parsed = parse_problem_text(pgml_pg)
    assert "Compute the derivative" in parsed.student[0]
    assert parsed.student[0].endswith("[INPUT]")
    assert parsed.solutions == ["The derivative is 2 {a} x + {b}."]
