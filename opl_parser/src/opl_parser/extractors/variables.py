"""Variable and helper extraction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence
import re

ASSIGNMENT_PATTERN = re.compile(r"(?P<sigil>[$@%])(?P<name>[A-Za-z][\w]*)\s*=\s*(?P<value>[^;]+);")
CONTEXT_PATTERN = re.compile(r"Context\(([^)]+)\)")
SUB_PATTERN = re.compile(r"sub\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", re.MULTILINE)
LOAD_PATTERN = re.compile(r"loadMacros\((.*?)\);", re.DOTALL)


@dataclass
class Assignment:
    name: str
    sigil: str
    value: str
    type: str


@dataclass
class VariableSummary:
    assignments: List[Assignment]
    contexts: Sequence[str]
    macros: Sequence[str]
    subroutines: Dict[str, str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "assignments": [
                {
                    "name": assignment.name,
                    "sigil": assignment.sigil,
                    "value": assignment.value,
                    "type": assignment.type,
                }
                for assignment in self.assignments
            ],
            "contexts": list(self.contexts),
            "macros": list(self.macros),
            "subroutines": self.subroutines,
        }


def _infer_value_type(value: str) -> str:
    lowered = value.lower()
    if "random" in lowered:
        return "random"
    if "rand" in lowered and "random" not in lowered:
        return "random"
    if any(op in lowered for op in ["+", "-", "*", "/", "**"]):
        return "expression"
    numeric = lowered.replace(".", "").replace("-", "")
    if numeric.isdigit():
        return "constant"
    return "unknown"


def _parse_assignments(content: str) -> List[Assignment]:
    assignments: List[Assignment] = []
    for match in ASSIGNMENT_PATTERN.finditer(content):
        sigil = match.group("sigil")
        name = match.group("name")
        value = match.group("value").strip()
        assignments.append(Assignment(name=name, sigil=sigil, value=value, type=_infer_value_type(value)))
    return assignments


def _parse_contexts(content: str) -> Sequence[str]:
    contexts: List[str] = []
    for match in CONTEXT_PATTERN.finditer(content):
        value = match.group(1).strip().strip('"\'')
        if value:
            contexts.append(value)
    return tuple(dict.fromkeys(contexts))


def _parse_subroutines(content: str) -> Dict[str, str]:
    subs: Dict[str, str] = {}
    for match in SUB_PATTERN.finditer(content):
        name = match.group(1)
        start = match.end()
        depth = 1
        index = start
        while index < len(content) and depth > 0:
            if content[index] == '{':
                depth += 1
            elif content[index] == '}':
                depth -= 1
            index += 1
        body = content[start:index - 1].strip()
        subs[name] = body
    return subs


def _parse_macros(content: str) -> Sequence[str]:
    macros: List[str] = []
    for match in LOAD_PATTERN.finditer(content):
        args = match.group(1)
        for raw in re.split(r",", args):
            cleaned = raw.strip().strip('"\'')
            if cleaned:
                macros.append(cleaned)
    return tuple(dict.fromkeys(macros))


def parse_variables(content: str) -> VariableSummary:
    """Return a structured summary of variable setup and helpers."""
    assignments = _parse_assignments(content)
    contexts = _parse_contexts(content)
    macros = _parse_macros(content)
    subroutines = _parse_subroutines(content)
    return VariableSummary(
        assignments=assignments,
        contexts=contexts,
        macros=macros,
        subroutines=subroutines,
    )

