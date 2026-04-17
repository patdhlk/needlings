"""Verify by invoking the `ubc` binary."""
from __future__ import annotations

import subprocess
from pathlib import Path

from needlings.backends.base import Backend, VerifyResult
from needlings.models import Exercise


LICENSE_HINT = (
    "ubc reports no active license. needlings is open source, and useblocks "
    "grants free license keys for OSS use — see the README for the request link, "
    "then run `ubc license activate <KEY>`."
)


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

        summary = f"ubc check exited {proc.returncode}"
        combined = (proc.stdout + "\n" + proc.stderr).lower()
        if "license" in combined:
            summary = LICENSE_HINT
        return VerifyResult.failure(
            self.name, stdout=proc.stdout, stderr=proc.stderr, summary=summary,
        )
