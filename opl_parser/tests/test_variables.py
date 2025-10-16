from __future__ import annotations

from opl_parser.extractors.variables import parse_variables


def test_parse_variables_assignments(classic_pg: str) -> None:
    summary = parse_variables(classic_pg)
    assignments = {assignment.name: assignment for assignment in summary.assignments}
    assert "radius" in assignments
    assert assignments["radius"].type == "random"
    assert assignments["circumference"].type == "expression"


def test_parse_variables_macros(pgml_pg: str) -> None:
    summary = parse_variables(pgml_pg)
    assert "PGML.pl" in summary.macros
