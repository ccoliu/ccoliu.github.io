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

from codoctopus.domains import Domain
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


class FakeDomain(Domain):
    name = "testdomain"
    roles = {"CODER": "You are a meticulous coder.", "REVIEWER": "You review code for bugs."}
    default_tools = ["read_file", "run_tests"]
    planner_hint = "Always end with a REVIEWER step."


def plan_using_named_roles() -> Plan:
    return Plan.model_validate(
        {
            "goal": "ship the feature",
            "steps": [
                {"key": "write", "name": "write", "role": "CODER", "instruction": "write the code"},
                {
                    "key": "review",
                    "name": "review",
                    "role": "REVIEWER",
                    "instruction": "review it",
                    "depends_on": ["write"],
                },
                {
                    "key": "note",
                    "name": "note",
                    "role": "a role the domain doesn't define",
                    "instruction": "leave a note",
                    "depends_on": ["review"],
                },
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


async def test_a_plan_with_no_domain_is_tagged_general():
    provider = ScriptedProvider(plans=[valid_plan()])

    plan = await make_plan(provider, "ship the feature")

    assert plan.domain == "general"


# --- domain wiring -------------------------------------------------------


async def test_domain_roles_and_hint_reach_the_planner_prompt():
    provider = ScriptedProvider(plans=[plan_using_named_roles()])

    await make_plan(provider, "ship the feature", domain=FakeDomain())

    system = provider.calls[0]["system"]
    assert "CODER" in system
    assert "REVIEWER" in system
    assert "Always end with a REVIEWER step." in system
    assert "run_tests" in system


async def test_a_recognized_role_name_is_expanded_to_its_full_prompt():
    provider = ScriptedProvider(plans=[plan_using_named_roles()])

    plan = await make_plan(provider, "ship the feature", domain=FakeDomain())

    by_key = {s.key: s for s in plan.steps}
    assert by_key["write"].role == "You are a meticulous coder."
    assert by_key["review"].role == "You review code for bugs."


async def test_a_role_the_domain_does_not_recognize_is_left_untouched():
    provider = ScriptedProvider(plans=[plan_using_named_roles()])

    plan = await make_plan(provider, "ship the feature", domain=FakeDomain())

    by_key = {s.key: s for s in plan.steps}
    assert by_key["note"].role == "a role the domain doesn't define"


async def test_the_returned_plan_is_tagged_with_the_domain_name():
    provider = ScriptedProvider(plans=[plan_using_named_roles()])

    plan = await make_plan(provider, "ship the feature", domain=FakeDomain())

    assert plan.domain == "testdomain"
