from pathlib import Path
from unittest.mock import patch

from needlings.backends.sphinx_backend import SphinxBackend
from needlings.models import Exercise, ExerciseId, VerifyConfig


def _ex() -> Exercise:
    return Exercise(
        id=ExerciseId("01-setup", "01-hello"),
        name="x", order=1, hint="h", sentinel="",
        verify=VerifyConfig(backend=["sphinx"], flags=["-W"]),
    )


def test_sphinx_backend_success(tmp_path: Path) -> None:
    backend = SphinxBackend()
    with patch("needlings.backends.sphinx_backend.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "ok"
        run.return_value.stderr = ""
        result = backend.run(build_dir=tmp_path, exercise=_ex())

    assert result.passed
    assert result.backend == "sphinx"
    args, _ = run.call_args
    assert "-W" in args[0]
    assert "-b" in args[0]
    assert "html" in args[0]


def test_sphinx_backend_failure(tmp_path: Path) -> None:
    backend = SphinxBackend()
    with patch("needlings.backends.sphinx_backend.subprocess.run") as run:
        run.return_value.returncode = 2
        run.return_value.stdout = ""
        run.return_value.stderr = "WARNING: treated as error\n"
        result = backend.run(build_dir=tmp_path, exercise=_ex())
    assert not result.passed
    assert "WARNING" in result.stderr
