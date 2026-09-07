from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from codoctopus.llm import Completion, Provider
from codoctopus.planning.models import Plan, PlanStep
from codoctopus.runtime import LocalExecutor, PlanResult


class ScriptedProvider(Provider):
    name = "scripted"
    default_model = "scripted-1"

    def __init__(self, responses: dict[str, str] | None = None, **options: Any) -> None:
        super().__init__("scripted-1", **options)
        self.responses = responses or {}
        self.calls: list[dict[str, Any]] = []

    async def _complete(self, messages, *, system, tools, output_schema, max_tokens, **kwargs) -> Completion:
        user_msg = messages[-1].content if messages and messages[-1].content else ""
        self.calls.append({"messages": list(messages), "system": system, "task": user_msg})
        
        reply = self.responses.get(user_msg, f"response for: {user_msg}")
        return Completion(text=reply, model=self.model)


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return tmp_path


@pytest.mark.anyio
async def test_linear_plan_execution(workspace: Path):
    provider = ScriptedProvider(
        responses={
            "step 1 instruction": "result 1",
            "step 2 using result 1": "result 2",
        }
    )
    plan = Plan(
        goal="run linear steps",
        steps=[
            PlanStep(key="s1", name="Step 1", role="role 1", instruction="step 1 instruction"),
            PlanStep(
                key="s2",
                name="Step 2",
                role="role 2",
                instruction="step 2 using {{steps.s1.result}}",
                depends_on=["s1"],
            ),
        ],
    )
    executor = LocalExecutor(provider, workspace=workspace)
    result = await executor.run(plan)

    assert result.status == "success"
    assert result.step_results["s1"] == "result 1"
    assert result.step_results["s2"] == "result 2"


@pytest.mark.anyio
async def test_parallel_independent_steps(workspace: Path):
    provider = ScriptedProvider(
        responses={
            "task A": "out A",
            "task B": "out B",
        }
    )
    plan = Plan(
        goal="run parallel steps",
        steps=[
            PlanStep(key="a", name="A", role="rA", instruction="task A"),
            PlanStep(key="b", name="B", role="rB", instruction="task B"),
        ],
    )
    executor = LocalExecutor(provider, workspace=workspace)
    result = await executor.run(plan)

    assert result.status == "success"
    assert result.step_results["a"] == "out A"
    assert result.step_results["b"] == "out B"


@pytest.mark.anyio
async def test_for_each_dynamic_expansion(workspace: Path):
    provider = ScriptedProvider(
        responses={
            "list items": '["apple", "banana"]',
            "process item: apple": "apple processed",
            "process item: banana": "banana processed",
        }
    )
    plan = Plan(
        goal="run for_each steps",
        steps=[
            PlanStep(key="producer", name="Producer", role="rp", instruction="list items"),
            PlanStep(
                key="consumer",
                name="Consumer",
                role="rc",
                instruction="process item: {{item}}",
                depends_on=[],
                for_each="producer",
            ),
        ],
    )
    executor = LocalExecutor(provider, workspace=workspace)
    result = await executor.run(plan)

    assert result.status == "success"
    assert result.step_results["producer"] == '["apple", "banana"]'
    assert result.step_results["consumer[0]"] == "apple processed"
    assert result.step_results["consumer[1]"] == "banana processed"


@pytest.mark.anyio
async def test_step_failure_stops_execution(workspace: Path):
    class FailingProvider(Provider):
        name = "failing"
        default_model = "failing-1"

        async def _complete(self, messages, *, system, tools, output_schema, max_tokens, **kwargs) -> Completion:
            raise RuntimeError("API connection failure")

    plan = Plan(
        goal="fail gracefully",
        steps=[
            PlanStep(key="s1", name="S1", role="r1", instruction="fail me"),
            PlanStep(key="s2", name="S2", role="r2", instruction="will not run", depends_on=["s1"]),
        ],
    )
    executor = LocalExecutor(FailingProvider("failing-1"), workspace=workspace)
    result = await executor.run(plan)

    assert result.status == "failed"
    assert "API connection failure" in (result.error or "")
    assert "s1" not in result.step_results
    assert "s2" not in result.step_results

@pytest.mark.anyio
async def test_plans_with_cyclic_dependency(workspace: Path):
    provider = ScriptedProvider(
        responses={
            "instruction 1": "instruction 1",
            "instruction 2": "instruction 2",
        }
    )
    cyclic_plan = Plan(
        goal="fail gracefully",
        steps=[
            PlanStep(key="s1", name="S1", role="r1", instruction="instruction 1", depends_on=["s2"]),
            PlanStep(key="s2", name="S2", role="r2", instruction="instruction 2", depends_on=["s1"]),
        ],
    )
    
    executor = LocalExecutor(provider, workspace=workspace)
    result = await executor.run(cyclic_plan)

    assert result.status == "failed"
    assert "circular dependency" in (result.error or "")
    assert "s1" not in result.step_results
    assert "s2" not in result.step_results
    

