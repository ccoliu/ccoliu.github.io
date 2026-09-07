# ---------------------------------------------------
# Codoctopus — Planner tests
#
# Same ScriptedProvider pattern as the other test files: no API key needed.
# The interesting case is the retry loop — a plan can be schema-valid (every
# field has the right type) and still be semantically broken (a cycle, a
# dangling dependency), and only the second kind of problem is caught here
# rather than by the LLM layer's own structured-output machinery.
# ---------------------------------------------------

from __future__ import annotations

from typing import Any

import pytest

from codoctopus.llm import Completion, Provider
from codoctopus.planning import Plan, PlanningError, make_plan


class ScriptedProvider(Provider):
    name = "scripted"
    default_model = "scripted-1"

    def __init__(self, model: str | None = None, *, plans: list[Plan] | None = None, **options: Any) -> None:
        super().__init__(model, **options)
        self._plans = list(plans or [])
        self.calls: list[dict[str, Any]] = []

    @property
    def supports_structured_output(self) -> bool:
        return True

    async def _complete(self, messages, *, system, tools, output_schema, max_tokens, **kwargs) -> Completion:
        self.calls.append({"messages": list(messages), "system": system})
        plan = self._plans.pop(0)
        return Completion(text=plan.model_dump_json(), model=self.model, parsed=plan)


def valid_plan() -> Plan:
    return Plan.model_validate(
        {
            "goal": "ship the feature",
            "steps": [
                {"key": "write", "name": "write", "role": "coder", "instruction": "write the code"},
                {
                    "key": "test",
                    "name": "test",
                    "role": "tester",
                    "instruction": "run the tests",
                    "depends_on": ["write"],
                },
            ],
        }
    )


def cyclic_plan() -> Plan:
    return Plan.model_validate(
        {
            "goal": "ship the feature",
            "steps": [
                {"key": "a", "name": "a", "role": "x", "instruction": "do a", "depends_on": ["b"]},
                {"key": "b", "name": "b", "role": "x", "instruction": "do b", "depends_on": ["a"]},
            ],
        }
    )


async def test_a_valid_plan_is_returned_on_the_first_try():
    provider = ScriptedProvider(plans=[valid_plan()])

    plan = await make_plan(provider, "ship the feature")

    assert plan.goal == "ship the feature"
    assert [s.key for s in plan.steps] == ["write", "test"]
    assert len(provider.calls) == 1


async def test_an_invalid_plan_is_retried_with_the_validation_error():
    provider = ScriptedProvider(plans=[cyclic_plan(), valid_plan()])

    plan = await make_plan(provider, "ship the feature")

    assert plan.steps[0].key == "write"
    assert len(provider.calls) == 2
    retry_prompt = provider.calls[1]["messages"][-1].content
    assert "circular dependency" in retry_prompt


async def test_planning_gives_up_after_the_retry_budget():
    provider = ScriptedProvider(plans=[cyclic_plan(), cyclic_plan(), cyclic_plan()])

    with pytest.raises(PlanningError, match="circular dependency"):
        await make_plan(provider, "ship the feature", max_retries=2)

    assert len(provider.calls) == 3
