# ---------------------------------------------------
# Codoctopus — Plan schema
#
# This is what replaces v1's WORKSHEET_FORMAT: instead of asking the model for
# prose in a specific shape and then slicing it with startswith(), the model
# is asked for this schema directly via structured output (codoctopus.llm),
# so a malformed plan is rejected by the API before it ever reaches a runner.
#
# `role` is plain system-prompt text for now, not a name looked up in a
# registry — that indirection belongs to domain packs (M4). Keeping it a raw
# string means Planner and Executor need nothing from a Domain to work today.
# ---------------------------------------------------

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    """
    One node in a Plan's dependency graph.

    `instruction` may reference another step's completed output with
    "{{steps.<key>.result}}", and — for a step whose `for_each` is set — the
    current item with "{{item}}" / "{{item.<field>}}". Both placeholder forms
    match Coworkify's own templating so the two systems stay easy to hold in
    your head together; rendering them is the executor's job, not the
    planner's.
    """

    key: str = Field(description="Identifier for this step, unique within the plan")
    name: str = Field(description="Short human-readable label")
    role: str = Field(description="System prompt this step's agent runs under")
    instruction: str = Field(description="The concrete task for this step to perform")
    depends_on: list[str] = Field(default_factory=list, description="Keys of steps that must finish first")
    tools: list[str] = Field(default_factory=list, description="Names of tools this step's agent may use")
    for_each: str | None = Field(
        default=None,
        description=(
            "Key of a step whose result is a list. When set, this step runs once per "
            "item in that list instead of once."
        ),
    )


class Plan(BaseModel):
    goal: str = Field(description="The goal this plan exists to accomplish")
    domain: str = Field(default="general", description="Which domain pack's conventions this plan follows")
    steps: list[PlanStep] = Field(min_length=1)
