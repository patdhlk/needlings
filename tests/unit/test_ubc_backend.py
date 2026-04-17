from pathlib import Path
from unittest.mock import patch

from needlings.backends.ubc_backend import UbcBackend
from needlings.models import Exercise, ExerciseId, VerifyConfig


def _ex() -> Exercise:
    return Exercise(
        id=ExerciseId("06-schema", "01-first"), name="x", order=1, hint="",
        sentinel="", verify=VerifyConfig(backend=["ubc"]),
    )


def test_ubc_backend_success(tmp_path: Path) -> None:
    backend = UbcBackend(binary="ubc")
    with patch("needlings.backends.ubc_backend.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "clean\n"
        run.return_value.stderr = ""
        result = backend.run(build_dir=tmp_path, exercise=_ex())
    assert result.passed


def test_ubc_backend_failure(tmp_path: Path) -> None:
    backend = UbcBackend(binary="ubc")
    with patch("needlings.backends.ubc_backend.subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stdout = "violation\n"
        run.return_value.stderr = ""
        result = backend.run(build_dir=tmp_path, exercise=_ex())
    assert not result.passed
    assert result.stdout == "violation\n"
    assert result.stderr == ""


def test_ubc_backend_license_hint(tmp_path: Path) -> None:
    backend = UbcBackend(binary="ubc")
    with patch("needlings.backends.ubc_backend.subprocess.run") as run:
        run.return_value.returncode = 2
        run.return_value.stdout = ""
        run.return_value.stderr = "ERROR: no active license\n"
        result = backend.run(build_dir=tmp_path, exercise=_ex())
    assert not result.passed
    assert "license" in result.summary.lower()
    assert "open source" in result.summary.lower()


def test_ubc_backend_binary_missing(tmp_path: Path) -> None:
    backend = UbcBackend(binary="ubc")
    with patch("needlings.backends.ubc_backend.subprocess.run",
               side_effect=FileNotFoundError):
        result = backend.run(build_dir=tmp_path, exercise=_ex())
    assert not result.passed
    assert "not found" in result.summary.lower()
