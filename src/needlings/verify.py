"""Dispatch to verification backends in order; short-circuit on first failure."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from needlings.backends.assertion_backend import AssertionBackend
from needlings.backends.base import Backend, VerifyResult
from needlings.backends.sphinx_backend import SphinxBackend
from needlings.backends.ubc_backend import UbcBackend
from needlings.models import Exercise


@dataclass
class VerifyOrchestrator:
    backends: dict[str, Backend]

    @classmethod
    def default(cls, *, ubc_binary: str = "ubc") -> VerifyOrchestrator:
        return cls({
            "sphinx": SphinxBackend(),
            "ubc": UbcBackend(binary=ubc_binary),
            "assertions": AssertionBackend(),
        })

    def run(self, *, build_dir: Path, exercise: Exercise) -> list[VerifyResult]:
        results: list[VerifyResult] = []
        for name in exercise.verify.backend:
            backend = self.backends.get(name)
            if backend is None:
                raise RuntimeError(f"unknown backend {name!r}")
            result = backend.run(build_dir=build_dir, exercise=exercise)
            results.append(result)
            if not result.passed:
                break
        return results

    def all_passed(self, results: list[VerifyResult]) -> bool:
        return bool(results) and all(r.passed for r in results)
