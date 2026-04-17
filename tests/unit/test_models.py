from needlings.models import Assertion, Exercise, ExerciseId, VerifyConfig


def test_exercise_id_roundtrip() -> None:
    eid = ExerciseId(chapter="01-setup", slug="01-hello-need")
    assert str(eid) == "01-setup/01-hello-need"
    assert ExerciseId.parse("01-setup/01-hello-need") == eid


def test_exercise_id_rejects_bad_format() -> None:
    import pytest

    with pytest.raises(ValueError):
        ExerciseId.parse("01-setup")


def test_verify_config_defaults() -> None:
    vc = VerifyConfig(backend=["sphinx"])
    assert vc.flags == []
    assert vc.assertions == []


def test_exercise_construction() -> None:
    ex = Exercise(
        id=ExerciseId("01-setup", "01-hello-need"),
        name="Hello, need",
        order=1,
        hint="Write a req directive.",
        sentinel=".. I AM NOT DONE",
        verify=VerifyConfig(
            backend=["sphinx", "assertions"],
            flags=["-W"],
            assertions=[Assertion(type="need_exists", params={"id": "REQ_HELLO"})],
        ),
    )
    assert ex.name == "Hello, need"
    assert ex.verify.backend == ["sphinx", "assertions"]
    assert ex.verify.assertions[0].params["id"] == "REQ_HELLO"
