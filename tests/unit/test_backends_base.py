# tests/unit/test_backends_base.py
from pathlib import Path

import pytest

from needlings.backends import Backend, VerifyResult
from needlings.models import Exercise, ExerciseId, VerifyConfig


def _dummy_exercise() -> Exercise:
    return Exercise(
        id=ExerciseId("01-setup", "01-hello"),
        name="hello",
        order=1,
        hint="",
        sentinel=".. I AM NOT DONE",
        verify=VerifyConfig(backend=["test"]),
    )


def test_verify_result_success_factory() -> None:
    r = VerifyResult.success("sphinx", summary="ok")
    assert r.backend == "sphinx"
    assert r.passed is True
    assert r.stdout == ""
    assert r.stderr == ""
    assert r.summary == "ok"


def test_verify_result_success_preserves_streams() -> None:
    r = VerifyResult.success("sphinx", stdout="build log", stderr="warnings", summary="ok")
    assert r.passed is True
    assert r.stdout == "build log"
    assert r.stderr == "warnings"


def test_verify_result_failure_factory() -> None:
    r = VerifyResult.failure("sphinx", stdout="out", stderr="err", summary="boom")
    assert r.passed is False
    assert r.stdout == "out"
    assert r.stderr == "err"
    assert r.summary == "boom"


def test_backend_subclass_without_name_raises() -> None:
    with pytest.raises(TypeError, match="name"):
        class Broken(Backend):
            def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
                return VerifyResult.success(self.name)


def test_backend_subclass_with_empty_name_raises() -> None:
    with pytest.raises(TypeError, match="name"):
        class Empty(Backend):
            name = ""

            def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
                return VerifyResult.success(self.name)


def test_backend_subclass_with_name_instantiates() -> None:
    class Good(Backend):
        name = "good"

        def run(self, *, build_dir: Path, exercise: Exercise) -> VerifyResult:
            return VerifyResult.success(self.name)

    backend = Good()
    assert backend.name == "good"
    result = backend.run(build_dir=Path("/tmp"), exercise=_dummy_exercise())
    assert result.passed is True
    assert result.backend == "good"
