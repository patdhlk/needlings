from needlings.backends.assertions import evaluate
from needlings.models import Assertion


NEEDS_JSON = {
    "versions": {
        "1.0": {
            "needs": {
                "REQ_HELLO": {
                    "id": "REQ_HELLO", "type": "req", "status": "open",
                    "links": ["SPEC_HELLO"], "title": "Hello",
                },
                "SPEC_HELLO": {
                    "id": "SPEC_HELLO", "type": "spec", "status": "open",
                    "links": [], "title": "Spec",
                },
            },
        },
    },
    "current_version": "1.0",
}

FLAT_NEEDS_JSON = {
    "needs": {
        "REQ_FLAT": {"id": "REQ_FLAT", "type": "req", "status": "open", "links": []},
    }
}


def test_need_exists_passes() -> None:
    ok, msg = evaluate(Assertion("need_exists", {"id": "REQ_HELLO"}), NEEDS_JSON)
    assert ok, msg


def test_need_exists_fails() -> None:
    ok, msg = evaluate(Assertion("need_exists", {"id": "MISSING"}), NEEDS_JSON)
    assert not ok
    assert "MISSING" in msg


def test_need_exists_flat_layout() -> None:
    ok, msg = evaluate(Assertion("need_exists", {"id": "REQ_FLAT"}), FLAT_NEEDS_JSON)
    assert ok, msg


def test_need_field_equals() -> None:
    a = Assertion("need_field_equals",
                  {"id": "REQ_HELLO", "field": "status", "value": "open"})
    ok, _ = evaluate(a, NEEDS_JSON)
    assert ok


def test_need_field_equals_mismatch() -> None:
    a = Assertion("need_field_equals",
                  {"id": "REQ_HELLO", "field": "status", "value": "closed"})
    ok, msg = evaluate(a, NEEDS_JSON)
    assert not ok
    assert "open" in msg


def test_link_exists() -> None:
    a = Assertion("link_exists",
                  {"from": "REQ_HELLO", "to": "SPEC_HELLO", "type": "links"})
    ok, _ = evaluate(a, NEEDS_JSON)
    assert ok


def test_link_exists_missing() -> None:
    a = Assertion("link_exists",
                  {"from": "REQ_HELLO", "to": "NOPE", "type": "links"})
    ok, _ = evaluate(a, NEEDS_JSON)
    assert not ok


def test_unknown_assertion_type() -> None:
    ok, msg = evaluate(Assertion("does_not_exist", {}), NEEDS_JSON)
    assert not ok
    assert "does_not_exist" in msg


def test_todo_absent_passes() -> None:
    doc = {"needs": {"X": {"content": "all done", "description": ""}}}
    ok, _ = evaluate(Assertion("todo_absent", {}), doc)
    assert ok


def test_todo_absent_detects_substring() -> None:
    doc = {"needs": {"X": {"content": ".. todo:: finish me", "description": ""}}}
    ok, msg = evaluate(Assertion("todo_absent", {}), doc)
    assert not ok
    assert "todo" in msg.lower()


def test_schema_violation_count_zero_passes() -> None:
    ok, _ = evaluate(Assertion("schema_violation_count", {"count": 0}), NEEDS_JSON)
    assert ok


def test_assertion_missing_param_returns_failure() -> None:
    # Required params should surface as failures, not raw KeyError.
    ok, msg = evaluate(Assertion("need_exists", {}), NEEDS_JSON)
    assert not ok
    assert "missing" in msg.lower() or "required" in msg.lower()
