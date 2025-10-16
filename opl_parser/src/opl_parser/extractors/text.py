"""Problem body extraction utilities."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

BLOCK_DELIMITERS = {
    "BEGIN_TEXT": "END_TEXT",
    "BEGIN_PGML": "END_PGML",
    "BEGIN_PGML_SOLUTION": "END_PGML_SOLUTION",
    "BEGIN_SOLUTION": "END_SOLUTION",
}

STUDENT_BLOCKS = {"BEGIN_TEXT", "BEGIN_PGML"}
SOLUTION_BLOCKS = {"BEGIN_SOLUTION", "BEGIN_PGML_SOLUTION"}

BEGIN_PATTERN = re.compile("|".join(re.escape(token) for token in sorted(BLOCK_DELIMITERS.keys(), key=len, reverse=True)))

ANSWER_WIDGETS = [
    re.compile(r"\\\{[^{}]*ans_rule[^{}]*\\\}", re.IGNORECASE),
    re.compile(r"\\\{[^{}]*ans_array[^{}]*\\\}", re.IGNORECASE),
    re.compile(r"\\\{[^{}]*essay_box[^{}]*\\\}", re.IGNORECASE),
    re.compile(r"\\\{[^{}]*matrix_entry_box[^{}]*\\\}", re.IGNORECASE),
    re.compile(r"\\\{[^{}]*multianswer[^{}]*\\\}", re.IGNORECASE),
]

PGML_BLANK_PATTERN = re.compile(r"\[_+\](?:\{\d*\})?")
BR_PATTERN = re.compile(r"\$BR\b")
PAR_PATTERN = re.compile(r"\$PAR\b")
VAR_PATTERN = re.compile(r"\$([A-Za-z][A-Za-z0-9_]*)")
TEX_DELIMS = [
    (re.compile(r"\\\("), ""),
    (re.compile(r"\\\)"), ""),
    (re.compile(r"\[``"), ""),
    (re.compile(r"``]"), ""),
]
WHITESPACE_CLEANUP = re.compile(r"\n{3,}")


@dataclass
class ProblemText:
    student: List[str]
    solutions: List[str]

    def as_dict(self) -> Dict[str, List[str]]:
        return {"student": self.student, "solutions": self.solutions}


def _find_block(content: str, start: int, begin_token: str) -> tuple[int, str]:
    end_token = BLOCK_DELIMITERS[begin_token]
    end_pattern = re.compile(re.escape(end_token))
    end_match = end_pattern.search(content, start)
    if not end_match:
        return len(content), ""
    block = content[start:end_match.start()]
    return end_match.end(), block


def _clean_block(block: str) -> str:
    text = block
    for pattern in ANSWER_WIDGETS:
        text = pattern.sub("[INPUT]", text)
    text = PGML_BLANK_PATTERN.sub("[INPUT]", text)
    text = text.replace("[INPUT]{}", "[INPUT]")
    text = BR_PATTERN.sub("\n", text)
    text = PAR_PATTERN.sub("\n\n", text)
    for pattern, replacement in TEX_DELIMS:
        text = pattern.sub(replacement, text)
    text = text.replace("[`", "")
    text = text.replace("`]", "")
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = VAR_PATTERN.sub(lambda match: f"{{{match.group(1)}}}", text)
    text = re.sub(r"\\n", "\n", text)
    text = re.sub(r"\\t", "\t", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = WHITESPACE_CLEANUP.sub("\n\n", text)
    return text.strip()


def parse_problem_text(content: str) -> ProblemText:
    """Extract student-facing and solution text blocks in document order."""
    student: List[str] = []
    solutions: List[str] = []

    position = 0
    while True:
        match = BEGIN_PATTERN.search(content, position)
        if not match:
            break
        begin_token = match.group(0)
        position, block = _find_block(content, match.end(), begin_token)
        cleaned = _clean_block(block)
        if not cleaned:
            continue
        if begin_token in STUDENT_BLOCKS:
            student.append(cleaned)
        elif begin_token in SOLUTION_BLOCKS:
            solutions.append(cleaned)

    return ProblemText(student=student, solutions=solutions)

