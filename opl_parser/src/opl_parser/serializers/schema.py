"""Data models for parsed problems."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional
import json


@dataclass
class AssignmentModel:
    name: str
    sigil: str
    value: str
    type: str


@dataclass
class VariableSummaryModel:
    assignments: List[AssignmentModel] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    macros: List[str] = field(default_factory=list)
    subroutines: Dict[str, str] = field(default_factory=dict)


@dataclass
class AnswerModel:
    expression: str
    type: str


@dataclass
class AnswerSummaryModel:
    answers: List[AnswerModel] = field(default_factory=list)
    graders: List[str] = field(default_factory=list)
    flags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProblemTextModel:
    student: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)


@dataclass
class ProblemRecord:
    file_path: str
    metadata: Dict[str, str]
    text: ProblemTextModel
    variables: VariableSummaryModel
    answers: AnswerSummaryModel
    macros: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    tags: Optional[List[str]] = None

    def dict(self) -> Dict[str, object]:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.dict(), ensure_ascii=False)

