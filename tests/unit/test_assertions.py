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


def test_need_exists_passes() -> None:
    ok, msg = evaluate(Assertion("need_exists", {"id": "REQ_HELLO"}), NEEDS_JSON)
    assert ok, msg


def test_need_exists_fails() -> None:
    ok, msg = evaluate(Assertion("need_exists", {"id": "MISSING"}), NEEDS_JSON)
    assert not ok
    assert "MISSING" in msg


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
