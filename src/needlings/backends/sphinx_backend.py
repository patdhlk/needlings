"""Verify by invoking `sphinx-build`."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from needlings.backends.base import Backend, VerifyResult
from needlings.models import Exercise


class SphinxBackend(Backend):
    name = "sphinx"

    def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
        out = build_dir / "_build" / "html"
        cmd = [
            sys.executable, "-m", "sphinx",
            "-b", "html",
            *exercise.verify.flags,
            str(build_dir), str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=build_dir)
        if proc.returncode == 0:
            return VerifyResult.success(self.name, summary="sphinx-build ok")
        return VerifyResult.failure(
            self.name,
            stdout=proc.stdout,
            stderr=proc.stderr,
            summary=f"sphinx-build exited {proc.returncode}",
        )
