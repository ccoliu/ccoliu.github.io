# ---------------------------------------------------
# Codoctopus — Plan validation tests
#
# Pure DAG-rule tests, no LLM involved. These mirror the cases Coworkify's
# WorkflowCreate validator already covers (tests/... in the coworkify repo),
# on purpose — the two are meant to agree on what counts as an executable plan.
# ---------------------------------------------------

from __future__ import annotations

import pytest

from codoctopus.planning.models import Plan, PlanStep
from codoctopus.planning.validate import PlanValidationError, validate_plan


def step(key: str, **kwargs) -> PlanStep:
    kwargs.setdefault("instruction", f"do {key}")
    return PlanStep(key=key, name=key, role="be helpful", **kwargs)


def plan(*steps: PlanStep) -> Plan:
    return Plan(goal="test", steps=list(steps))


# --- the happy paths ----------------------------------------------------


def test_a_linear_plan_is_valid():
    validate_plan(plan(step("a"), step("b", depends_on=["a"]), step("c", depends_on=["b"])))


def test_independent_steps_need_no_dependency():
    validate_plan(plan(step("a"), step("b")))


def test_a_for_each_group_may_depend_on_its_own_siblings():
    validate_plan(
        plan(
            step("search", instruction="find jobs"),
            step("tailor", for_each="search", depends_on=[]),
            step("apply", for_each="search", depends_on=["tailor"]),
        )
    )


# --- structural errors ---------------------------------------------------


def test_duplicate_keys_are_rejected():
    with pytest.raises(PlanValidationError, match="unique"):
        validate_plan(plan(step("a"), step("a")))


def test_a_dependency_on_an_unknown_step_is_rejected():
    with pytest.raises(PlanValidationError, match="unknown step 'nope'"):
        validate_plan(plan(step("a", depends_on=["nope"])))


def test_a_step_cannot_depend_on_itself():
    with pytest.raises(PlanValidationError, match="cannot depend on itself"):
        validate_plan(plan(step("a", depends_on=["a"])))


@pytest.mark.parametrize(
    "steps",
    [
        [step("a", depends_on=["b"]), step("b", depends_on=["a"])],
        [step("a", depends_on=["c"]), step("b", depends_on=["a"]), step("c", depends_on=["b"])],
    ],
    ids=["two-cycle", "three-cycle"],
)
def test_circular_dependencies_are_rejected(steps):
    with pytest.raises(PlanValidationError, match="circular dependency"):
        validate_plan(plan(*steps))


# --- for_each rules --------------------------------------------------------


def test_for_each_target_must_exist():
    with pytest.raises(PlanValidationError, match="unknown step 'nope'"):
        validate_plan(plan(step("a", for_each="nope")))


def test_a_step_cannot_for_each_itself():
    with pytest.raises(PlanValidationError, match="cannot for_each itself"):
        validate_plan(plan(step("a", for_each="a")))


def test_nested_for_each_is_rejected():
    with pytest.raises(PlanValidationError, match="nested expansion is not supported"):
        validate_plan(
            plan(
                step("search", instruction="find jobs"),
                step("outer", for_each="search"),
                step("inner", for_each="outer"),
            )
        )


def test_a_regular_step_cannot_fan_in_from_a_for_each_step():
    with pytest.raises(PlanValidationError, match="fan-in/reduce is not supported"):
        validate_plan(
            plan(
                step("search", instruction="find jobs"),
                step("tailor", for_each="search"),
                step("summarize", depends_on=["tailor"]),
            )
        )


def test_a_for_each_step_cannot_depend_on_a_step_outside_its_group():
    with pytest.raises(PlanValidationError, match="can only depend on other steps in that group"):
        validate_plan(
            plan(
                step("search", instruction="find jobs"),
                step("unrelated"),
                step("tailor", for_each="search", depends_on=["unrelated"]),
            )
        )
