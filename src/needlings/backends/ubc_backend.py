"""Verify by invoking the `ubc` binary."""
from __future__ import annotations

import subprocess
from pathlib import Path

from needlings.backends.base import Backend, VerifyResult
from needlings.models import Exercise


class UbcBackend(Backend):
    name = "ubc"

    def __init__(self, binary: str = "ubc") -> None:
        self.binary = binary

    def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
        # ubc check takes no per-exercise flags; exercise retained for Backend signature parity.
        try:
            proc = subprocess.run(
                [self.binary, "check", str(build_dir)],
                capture_output=True, text=True, cwd=build_dir,
            )
        except FileNotFoundError:
            return VerifyResult.failure(
                self.name,
                summary="ubc binary not found — install ubc and ensure it's on PATH.",
            )
        if proc.returncode == 0:
            return VerifyResult.success(self.name, summary="ubc check clean")

        return VerifyResult.failure(
            self.name,
            stdout=proc.stdout,
            stderr=proc.stderr,
            summary=f"ubc check exited {proc.returncode}",
        )
