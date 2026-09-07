# ---------------------------------------------------
# Codoctopus — Executor interface
#
# The contract every backend that can run a Plan must satisfy. LocalExecutor
# (asyncio, no infrastructure) and the future CoworkifyExecutor (Celery +
# Redis + Postgres) both implement this — a Plan means the same thing on
# either, since both are built against the same validate_plan() rules
# (codoctopus.planning.validate).
# ---------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

from codoctopus.planning.models import Plan

Status = Literal["success", "failed"]


@dataclass
class PlanResult:
    """What running a Plan produced."""

    plan: Plan
    status: Status
    #: step key -> that step's final text output (one entry per for_each item,
    #: keyed "<key>[<index>]", for a step that was dynamically expanded).
    step_results: dict[str, str] = field(default_factory=dict)
    error: str | None = None


@runtime_checkable
class Executor(Protocol):
    async def run(self, plan: Plan) -> PlanResult: ...
