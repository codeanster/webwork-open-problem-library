"""Answer and grading logic extraction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import re

ANS_PATTERN = re.compile(r"ANS(?:_NAME)?\((.*?)\);", re.DOTALL)
GRADER_PATTERN = re.compile(r"install_problem_grader\((.*?)\);", re.DOTALL)
FLAG_PATTERN = re.compile(r"\$(showPartialCorrectAnswers|partialCredit)\s*=\s*(\w+);")


@dataclass
class AnswerRule:
    expression: str
    type: str


@dataclass
class AnswerSummary:
    answers: List[AnswerRule]
    graders: List[str]
    flags: Dict[str, str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "answers": [
                {
                    "expression": answer.expression,
                    "type": answer.type,
                }
                for answer in self.answers
            ],
            "graders": self.graders,
            "flags": self.flags,
        }


def _infer_answer_type(expression: str) -> str:
    lowered = expression.lower()
    if "->cmp" in lowered:
        return "numeric"
    if "str_cmp" in lowered:
        return "string"
    if "radio_cmp" in lowered or "radio->cmp" in lowered:
        return "multiple_choice"
    if "checkbox_cmp" in lowered:
        return "checkbox"
    if "essay_cmp" in lowered:
        return "essay"
    if "matrix_cmp" in lowered:
        return "matrix"
    if "formula" in lowered:
        return "formula"
    return "unknown"


def parse_answers(content: str) -> AnswerSummary:
    answers: List[AnswerRule] = []
    for match in ANS_PATTERN.finditer(content):
        expression = match.group(1).strip()
        answers.append(AnswerRule(expression=expression, type=_infer_answer_type(expression)))

    graders = [match.group(1).strip() for match in GRADER_PATTERN.finditer(content)]

    flags: Dict[str, str] = {}
    for match in FLAG_PATTERN.finditer(content):
        name, value = match.groups()
        flags[name] = value

    return AnswerSummary(answers=answers, graders=graders, flags=flags)

