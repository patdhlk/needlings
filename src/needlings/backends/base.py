"""Base classes for verification backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from needlings.models import Exercise


@dataclass(frozen=True)
class VerifyResult:
    backend: str
    passed: bool
    stdout: str = ""
    stderr: str = ""
    summary: str = ""

    @classmethod
    def success(cls, backend: str, summary: str = "") -> VerifyResult:
        return cls(backend=backend, passed=True, summary=summary)

    @classmethod
    def failure(cls, backend: str, *, stdout: str = "", stderr: str = "",
                summary: str = "") -> VerifyResult:
        return cls(backend=backend, passed=False, stdout=stdout,
                   stderr=stderr, summary=summary)


class Backend(ABC):
    name: str

    @abstractmethod
    def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult: ...
