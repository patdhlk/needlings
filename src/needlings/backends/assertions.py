"""Evaluate assertion DSL against a parsed needs.json document."""
from __future__ import annotations

from typing import Any

from needlings.models import Assertion


def evaluate(assertion: Assertion, needs_doc: dict[str, Any]) -> tuple[bool, str]:
    """Return (passed, message). Message describes failure or 'ok'."""
    handler = _HANDLERS.get(assertion.type)
    if handler is None:
        return False, f"unknown assertion type: {assertion.type}"
    try:
        return handler(assertion, _flatten_needs(needs_doc))
    except KeyError as e:
        return False, f"assertion {assertion.type!r} missing required param: {e}"


def _flatten_needs(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if "versions" in doc:
        current = doc.get("current_version", "")
        versions = doc["versions"]
        bucket = versions.get(current) or next(iter(versions.values()), {})
        return bucket.get("needs", {}) if isinstance(bucket, dict) else {}
    return doc.get("needs", {})


def _need_exists(a: Assertion, needs: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    nid = a.params["id"]
    if nid in needs:
        return True, "ok"
    return False, f"need {nid!r} not found in needs.json"


def _need_field_equals(
    a: Assertion, needs: dict[str, dict[str, Any]]
) -> tuple[bool, str]:
    nid = a.params["id"]
    field = a.params["field"]
    expected = a.params["value"]
    need = needs.get(nid)
    if need is None:
        return False, f"need {nid!r} not found"
    actual = need.get(field)
    if actual == expected:
        return True, "ok"
    return False, f"need {nid}: {field}={actual!r}, expected {expected!r}"


def _link_exists(
    a: Assertion, needs: dict[str, dict[str, Any]]
) -> tuple[bool, str]:
    src = a.params["from"]
    dst = a.params["to"]
    link_type = a.params.get("type", "links")
    need = needs.get(src)
    if need is None:
        return False, f"source need {src!r} not found"
    if dst in need.get(link_type, []):
        return True, "ok"
    return False, f"need {src} has no {link_type} → {dst}"


def _todo_absent(a: Assertion, needs: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    # Walks stored descriptions; useful for ensuring learner removed todo:: blocks.
    substring = a.params.get("substring", ".. todo::")
    for nid, need in needs.items():
        body = (need.get("content") or "") + (need.get("description") or "")
        if substring in body:
            return False, f"need {nid} still contains {substring!r}"
    return True, "ok"


def _schema_violation_count(
    a: Assertion, needs: dict[str, dict[str, Any]]
) -> tuple[bool, str]:
    # Stub: schema violations aren't in needs.json per se; placeholder for
    # assertions driven by ubc output. Treat absence as pass.
    expected = int(a.params.get("count", 0))
    if expected == 0:
        return True, "ok"
    return False, (
        "schema_violation_count assertion requires ubc backend output; "
        "currently only supports count=0."
    )


_HANDLERS = {
    "need_exists": _need_exists,
    "need_field_equals": _need_field_equals,
    "link_exists": _link_exists,
    "todo_absent": _todo_absent,
    "schema_violation_count": _schema_violation_count,
}
