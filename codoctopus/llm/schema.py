# ---------------------------------------------------
# Codoctopus — JSON Schema helpers
#
# Providers that enforce structured output want a self-contained, strict schema:
# no $ref indirection, every property required, additionalProperties disabled.
# Pydantic emits $defs/$ref by default, so we inline and tighten it here once
# rather than in each adapter.
# ---------------------------------------------------

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def to_strict_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Render a pydantic model as a strict, fully inlined JSON Schema."""
    raw = model.model_json_schema()
    defs = raw.pop("$defs", {})
    return _tighten(_inline(raw, defs))


def _inline(node: Any, defs: dict[str, Any], seen: frozenset[str] = frozenset()) -> Any:
    """Replace every local $ref with the definition it points at."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.removeprefix("#/$defs/")
            if name in seen:
                # Recursive model: leave an open object rather than looping forever.
                return {"type": "object"}
            target = defs.get(name)
            if target is None:
                return {"type": "object"}
            merged = {**_inline(target, defs, seen | {name}), **{k: v for k, v in node.items() if k != "$ref"}}
            return merged
        return {k: _inline(v, defs, seen) for k, v in node.items()}
    if isinstance(node, list):
        return [_inline(item, defs, seen) for item in node]
    return node


def _tighten(node: Any) -> Any:
    """
    Make every fixed-shape object node strict.

    Strict mode has no notion of an optional property, so each one is listed in
    `required`; fields that are genuinely optional carry a null in their type
    union already, which is how absence is expressed.

    Only nodes with a `properties` key are fixed-shape objects and get this
    treatment. A pydantic `dict[str, X]` field renders as `{"type": "object",
    "additionalProperties": {...value schema...}}` with no `properties` key —
    that `additionalProperties` is the value schema, not a strictness flag, and
    must be left alone or the field becomes unusable (an object that may hold
    no keys at all).
    """
    if isinstance(node, dict):
        out = {k: _tighten(v) for k, v in node.items()}
        if "properties" in out:
            props = out["properties"]
            out.setdefault("type", "object")
            out["additionalProperties"] = False
            out["required"] = list(props.keys())
        return out
    if isinstance(node, list):
        return [_tighten(item) for item in node]
    return node
