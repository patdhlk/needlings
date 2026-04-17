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
    def success(cls, backend: str, *, stdout: str = "",
                stderr: str = "", summary: str = "") -> VerifyResult:
        return cls(backend=backend, passed=True, stdout=stdout,
                   stderr=stderr, summary=summary)

    @classmethod
    def failure(cls, backend: str, *, stdout: str = "", stderr: str = "",
                summary: str = "") -> VerifyResult:
        return cls(backend=backend, passed=False, stdout=stdout,
                   stderr=stderr, summary=summary)


class Backend(ABC):
    """Abstract verification backend. Subclasses must set a class-level string `name`."""

    name: str

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not isinstance(getattr(cls, "name", None), str) or not cls.name:
            raise TypeError(
                f"{cls.__name__} must define a non-empty class attribute 'name'."
            )

    @abstractmethod
    def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult: ...
