import json
from pathlib import Path
from unittest.mock import patch

from needlings.backends.assertion_backend import AssertionBackend
from needlings.models import Assertion, Exercise, ExerciseId, VerifyConfig


def _ex(*assertions: Assertion) -> Exercise:
    return Exercise(
        id=ExerciseId("01-setup", "01-hello"), name="x", order=1, hint="",
        sentinel="",
        verify=VerifyConfig(backend=["assertions"], assertions=list(assertions)),
    )


def _fake_needs_json(build_dir: Path) -> None:
    out = build_dir / "_needs_build"
    out.mkdir(parents=True)
    (out / "needs.json").write_text(json.dumps({
        "current_version": "1.0",
        "versions": {"1.0": {"needs": {
            "REQ_HELLO": {"id": "REQ_HELLO", "type": "req", "status": "open"},
        }}},
    }))


def test_assertion_backend_success(tmp_path: Path) -> None:
    backend = AssertionBackend()
    ex = _ex(Assertion("need_exists", {"id": "REQ_HELLO"}))

    def fake_run(*args, **kwargs):
        _fake_needs_json(tmp_path)
        class R:
            returncode = 0; stdout = ""; stderr = ""
        return R()

    with patch(
        "needlings.backends.assertion_backend.subprocess.run", side_effect=fake_run
    ):
        result = backend.run(build_dir=tmp_path, exercise=ex)
    assert result.passed


def test_assertion_backend_failure(tmp_path: Path) -> None:
    backend = AssertionBackend()
    ex = _ex(Assertion("need_exists", {"id": "MISSING"}))

    def fake_run(*args, **kwargs):
        _fake_needs_json(tmp_path)
        class R:
            returncode = 0; stdout = ""; stderr = ""
        return R()

    with patch(
        "needlings.backends.assertion_backend.subprocess.run", side_effect=fake_run
    ):
        result = backend.run(build_dir=tmp_path, exercise=ex)
    assert not result.passed
    assert "MISSING" in result.stderr
