from pathlib import Path
from unittest.mock import MagicMock

from needlings.backends.base import VerifyResult
from needlings.models import Exercise, ExerciseId, VerifyConfig
from needlings.verify import VerifyOrchestrator


def _ex(backends: list[str]) -> Exercise:
    return Exercise(
        id=ExerciseId("01", "01-x"), name="x", order=1, hint="", sentinel="",
        verify=VerifyConfig(backend=backends),
    )


def test_orchestrator_all_pass(tmp_path: Path) -> None:
    b1 = MagicMock(name="b1")
    b1.run.return_value = VerifyResult.success("sphinx")
    b2 = MagicMock(name="b2")
    b2.run.return_value = VerifyResult.success("assertions")

    orch = VerifyOrchestrator({"sphinx": b1, "assertions": b2})
    results = orch.run(build_dir=tmp_path, exercise=_ex(["sphinx", "assertions"]))

    assert [r.passed for r in results] == [True, True]
    b1.run.assert_called_once()
    b2.run.assert_called_once()


def test_orchestrator_short_circuits_on_failure(tmp_path: Path) -> None:
    b1 = MagicMock()
    b1.run.return_value = VerifyResult.failure("sphinx", stderr="nope")
    b2 = MagicMock()
    b2.run.return_value = VerifyResult.success("assertions")

    orch = VerifyOrchestrator({"sphinx": b1, "assertions": b2})
    results = orch.run(build_dir=tmp_path, exercise=_ex(["sphinx", "assertions"]))

    assert len(results) == 1
    assert not results[0].passed
    b2.run.assert_not_called()


def test_orchestrator_unknown_backend_raises(tmp_path: Path) -> None:
    import pytest
    orch = VerifyOrchestrator({})
    with pytest.raises(RuntimeError, match="unknown backend"):
        orch.run(build_dir=tmp_path, exercise=_ex(["nope"]))
