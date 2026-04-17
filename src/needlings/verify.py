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
        for backend_name in exercise.verify.backend:
            backend = self.backends.get(backend_name)
            if backend is None:
                raise RuntimeError(f"unknown backend {backend_name!r}")
            try:
                result = backend.run(build_dir=build_dir, exercise=exercise)
            except Exception as exc:  # noqa: BLE001
                result = VerifyResult.failure(
                    backend_name, summary=f"backend {backend_name!r} raised: {exc}"
                )
            results.append(result)
            if not result.passed:
                break
        return results

    @staticmethod
    def all_passed(results: list[VerifyResult]) -> bool:
        return bool(results) and all(r.passed for r in results)
