# ---------------------------------------------------
# Codoctopus — Plan validation
#
# Pure functions, no LLM involved — the same DAG rules Coworkify enforces in
# schemas/workflow.py's WorkflowCreate validator, ported here so a Plan means
# the same thing regardless of which Executor eventually runs it. If these
# rules and Coworkify's ever diverge, a plan built for one executor could
# silently misbehave on the other.
# ---------------------------------------------------

from __future__ import annotations

from codoctopus.planning.models import Plan, PlanStep


class PlanValidationError(ValueError):
    """A Plan's dependency graph is not executable."""


def validate_plan(plan: Plan) -> None:
    """Raise PlanValidationError if `plan` could not be scheduled by any executor."""
    steps = plan.steps
    keys = [s.key for s in steps]
    if len(keys) != len(set(keys)):
        raise PlanValidationError("step keys must be unique")

    key_set = set(keys)
    by_key = {s.key: s for s in steps}

    _validate_dependencies_exist(steps, key_set)
    _validate_for_each_rules(steps, key_set, by_key)
    _validate_no_cycles(steps, key_set)


def _validate_dependencies_exist(steps: list[PlanStep], key_set: set[str]) -> None:
    for step in steps:
        for dep in step.depends_on:
            if dep not in key_set:
                raise PlanValidationError(f"step '{step.key}' depends on unknown step '{dep}'")
            if dep == step.key:
                raise PlanValidationError(f"step '{step.key}' cannot depend on itself")


def _validate_for_each_rules(steps: list[PlanStep], key_set: set[str], by_key: dict[str, PlanStep]) -> None:
    for step in steps:
        if step.for_each is None:
            # A regular step may not fan in from a for_each step — the value
            # produced is a list of per-item results, not a single result, and
            # nothing here defines how to reduce it (no fan-in/reduce yet).
            for dep in step.depends_on:
                if by_key[dep].for_each is not None:
                    raise PlanValidationError(
                        f"step '{step.key}' depends on '{dep}', a for_each step "
                        "(fan-in/reduce is not supported)"
                    )
            continue

        if step.for_each not in key_set:
            raise PlanValidationError(f"step '{step.key}' has for_each pointing to unknown step '{step.for_each}'")
        if step.for_each == step.key:
            raise PlanValidationError(f"step '{step.key}' cannot for_each itself")
        if by_key[step.for_each].for_each is not None:
            raise PlanValidationError(
                f"step '{step.key}' has for_each on '{step.for_each}', which is itself a for_each "
                "step (nested expansion is not supported)"
            )
        # A for_each step's dependencies must all belong to the same group —
        # it cannot reach outside to a step that won't be expanded alongside it.
        for dep in step.depends_on:
            if by_key[dep].for_each != step.for_each:
                raise PlanValidationError(
                    f"step '{step.key}' is in the for_each='{step.for_each}' group; it can only "
                    f"depend on other steps in that group, not '{dep}'"
                )


def _validate_no_cycles(steps: list[PlanStep], key_set: set[str]) -> None:
    deps = {s.key: s.depends_on for s in steps}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in key_set}

    def dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        for dep in deps[node]:
            if color[dep] == GRAY:
                raise PlanValidationError("plan has a circular dependency: " + " -> ".join([*path, dep]))
            if color[dep] == WHITE:
                dfs(dep, [*path, dep])
        color[node] = BLACK

    for key in key_set:
        if color[key] == WHITE:
            dfs(key, [key])
