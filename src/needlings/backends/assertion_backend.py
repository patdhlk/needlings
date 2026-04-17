"""Run sphinx-build -b needs, then evaluate the DSL against needs.json."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from needlings.backends.assertions import evaluate
from needlings.backends.base import Backend, VerifyResult
from needlings.models import Exercise


class AssertionBackend(Backend):
    name = "assertions"

    def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
        out = build_dir / "_needs_build"
        cmd = [
            sys.executable, "-m", "sphinx",
            "-b", "needs", str(build_dir), str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=build_dir)
        needs_file = out / "needs.json"
        if proc.returncode != 0 or not needs_file.exists():
            return VerifyResult.failure(
                self.name, stdout=proc.stdout, stderr=proc.stderr,
                summary="sphinx-build -b needs failed before assertions could run",
            )

        doc = json.loads(needs_file.read_text())
        failures: list[str] = []
        for a in exercise.verify.assertions:
            ok, msg = evaluate(a, doc)
            if not ok:
                failures.append(f"  ✗ {a.type}: {msg}")

        if failures:
            return VerifyResult.failure(
                self.name, stderr="\n".join(failures),
                summary=f"{len(failures)} assertion(s) failed",
            )
        return VerifyResult.success(
            self.name, summary=f"{len(exercise.verify.assertions)} assertion(s) passed",
        )
