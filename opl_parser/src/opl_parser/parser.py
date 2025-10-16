"""High-level PG problem parser orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from .extractors import parse_answers, parse_metadata, parse_problem_text, parse_variables
from .extractors.variables import VariableSummary
from .extractors.metadata import parse_load_macros
from .serializers.schema import (
    AnswerModel,
    AnswerSummaryModel,
    AssignmentModel,
    ProblemRecord,
    ProblemTextModel,
    VariableSummaryModel,
)


@dataclass
class ParserConfig:
    root: Optional[Path] = None
    include_extensions: tuple[str, ...] = (".pg",)
    exclude_directories: tuple[str, ...] = ()


class PGProblemParser:
    """Parse PG files into structured records."""

    def __init__(self, config: Optional[ParserConfig] = None) -> None:
        self.config = config or ParserConfig()

    def _should_parse(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if self.config.include_extensions and path.suffix not in self.config.include_extensions:
            return False
        for part in path.parts:
            if part in self.config.exclude_directories:
                return False
        return True

    def _infer_tags(self, content: str, metadata: dict, variables: VariableSummary) -> list[str]:
        tags: list[str] = []
        lowered = content.lower()
        math_keywords = ["derivative", "integral", "function", "equation", "solve", "limit"]
        physics_keywords = ["velocity", "acceleration", "force", "energy", "momentum"]
        chemistry_keywords = ["mole", "concentration", "reaction", "equilibrium"]

        if any(keyword in lowered for keyword in math_keywords):
            tags.append("mathematics")
        if any(keyword in lowered for keyword in physics_keywords):
            tags.append("physics")
        if any(keyword in lowered for keyword in chemistry_keywords):
            tags.append("chemistry")

        difficulty = metadata.get("level")
        if difficulty:
            tags.append(f"level:{difficulty}")

        if len(variables.assignments) > 3:
            tags.append("complex")
        else:
            tags.append("basic")
        return tags

    def parse_file(self, path: Path) -> ProblemRecord:
        with Path(path).open("r", encoding="utf-8") as handle:
            content = handle.read()

        metadata = parse_metadata(content)
        text = parse_problem_text(content)
        variables = parse_variables(content)
        answers = parse_answers(content)
        macros = parse_load_macros(content)
        contexts = list(dict.fromkeys(variables.contexts))
        tags = self._infer_tags(content, metadata, variables)

        variables_dict = variables.as_dict()
        variable_model = VariableSummaryModel(
            assignments=[AssignmentModel(**assignment) for assignment in variables_dict["assignments"]],
            contexts=variables_dict["contexts"],
            macros=variables_dict["macros"],
            subroutines=variables_dict["subroutines"],
        )

        answers_dict = answers.as_dict()
        answer_model = AnswerSummaryModel(
            answers=[AnswerModel(**answer) for answer in answers_dict["answers"]],
            graders=answers_dict["graders"],
            flags=answers_dict["flags"],
        )

        record = ProblemRecord(
            file_path=str(path),
            metadata=metadata,
            text=ProblemTextModel(**text.as_dict()),
            variables=variable_model,
            answers=answer_model,
            macros=list(macros),
            contexts=contexts,
            tags=tags,
        )
        return record

    def iter_directory(self, root: Optional[Path] = None) -> Iterator[ProblemRecord]:
        root_path = Path(root or self.config.root or Path.cwd())
        for path in root_path.rglob("*"):
            if not self._should_parse(path):
                continue
            yield self.parse_file(path)

    def to_json(self, record: ProblemRecord) -> str:
        return record.json()

