"""Domain models for exercises, chapters, and verification config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExerciseId:
    chapter: str
    slug: str

    def __str__(self) -> str:
        return f"{self.chapter}/{self.slug}"

    @classmethod
    def parse(cls, s: str) -> ExerciseId:
        parts = s.split("/", maxsplit=1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"Invalid exercise id {s!r}: expected '<chapter>/<slug>'."
            )
        return cls(chapter=parts[0], slug=parts[1])


@dataclass(frozen=True)
class Assertion:
    type: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerifyConfig:
    backend: list[str]
    flags: list[str] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)


@dataclass(frozen=True)
class Exercise:
    id: ExerciseId
    name: str
    order: int
    hint: str
    sentinel: str
    verify: VerifyConfig
    # Absolute path to the exercise directory on disk.
    path: str = ""


@dataclass(frozen=True)
class Chapter:
    id: str                 # "01-setup"
    title: str
    exercises: list[Exercise]


@dataclass
class ExerciseState:
    completed_at: str | None = None
    attempts: int = 0
    hint_viewed: bool = False
