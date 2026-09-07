# ---------------------------------------------------
# Codoctopus — Planner
#
# Turns a goal into a validated Plan. Structured output (codoctopus.llm)
# guarantees the *shape* is right — field types, required keys — but DAG
# semantics (no cycles, dependencies exist, for_each rules) can't be expressed
# in a JSON Schema, so they're checked afterward and, on failure, fed back to
# the model for a corrected plan. Same retry-with-the-error shape as the LLM
# layer's own structured-output fallback (codoctopus.llm.base), just one
# level up, because a schema-valid Plan can still be a semantically broken one.
# ---------------------------------------------------

from __future__ import annotations

from codoctopus.llm.base import Provider
from codoctopus.llm.types import Message
from codoctopus.planning.models import Plan
from codoctopus.planning.validate import PlanValidationError, validate_plan

_SYSTEM_PROMPT = """You are a planner. Break the user's goal into a directed \
acyclic graph of steps for other agents to execute.

Each step needs:
- a stable "key" used to reference it from other steps
- a "role": the system prompt the step's agent should run under
- a concrete "instruction" describing exactly what to do
- "depends_on": keys of steps that must finish first (omit for steps that can \
start immediately or run in parallel)
- "tools": names of tools the step's agent may use, if any

Use "for_each" only when a step's result is a list and later steps must run \
once per item in it; reference the current item in a dependent step's \
instruction with "{{item}}" or "{{item.<field>}}". Reference another \
already-completed step's output with "{{steps.<key>.result}}".

Keep the plan as small as it can be while still fully accomplishing the goal."""


class PlanningError(RuntimeError):
    """The planner could not produce a valid Plan within its retry budget."""


async def make_plan(
    provider: Provider,
    goal: str,
    *,
    domain: str = "general",
    max_retries: int = 2,
) -> Plan:
    """Ask `provider` to decompose `goal` into a validated Plan."""
    messages = [Message.user(f"Goal: {goal}\nDomain: {domain}")]
    last_error: Exception | None = None

    for _ in range(max_retries + 1):
        completion = await provider.complete(messages, system=_SYSTEM_PROMPT, output_schema=Plan)
        plan = completion.parsed
        assert plan is not None, "output_schema was requested; the LLM layer guarantees a parsed result"

        try:
            validate_plan(plan)
            return plan
        except PlanValidationError as exc:
            last_error = exc
            messages = [
                *messages,
                completion.to_message(),
                Message.user(f"That plan is not valid: {exc}\nReturn a corrected plan."),
            ]

    raise PlanningError(f"could not produce a valid plan after {max_retries + 1} attempt(s): {last_error}")
