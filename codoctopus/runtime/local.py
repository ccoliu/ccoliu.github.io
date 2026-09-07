# ---------------------------------------------------
# Codoctopus — Local Executor
#
# Runs a Plan directly in the current process using asyncio.
# Handles DAG scheduling, step dependency resolution, instruction templating,
# and for_each expansion with zero external infrastructure.
# ---------------------------------------------------

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from codoctopus.agents import Agent
from codoctopus.llm import Provider
from codoctopus.planning.models import Plan, PlanStep
from codoctopus.planning.validate import validate_plan
from codoctopus.runtime.base import Executor, PlanResult
from codoctopus.tools import Tool, ToolRegistry


def _parse_list_output(raw: str) -> list[Any]:
    """Parse output into a list for for_each expansion."""
    raw = raw.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    # Fallback to lines
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _render_instruction(
    instruction: str,
    step_results: dict[str, str],
    *,
    item: Any | None = None,
) -> str:
    """Render {{steps.<key>.result}} and {{item}} / {{item.<field>}} in instruction."""
    rendered = instruction

    for key, result in step_results.items():
        rendered = rendered.replace(f"{{{{steps.{key}.result}}}}", str(result))

    if item is not None:
        rendered = rendered.replace("{{item}}", str(item))
        if isinstance(item, dict):
            for k, v in item.items():
                rendered = rendered.replace(f"{{{{item.{k}}}}}", str(v))

    return rendered


class LocalExecutor(Executor):
    """
    In-process executor for Plan DAGs using asyncio.

    - Resolves dependencies and executes ready steps concurrently.
    - Renders `{{steps.<key>.result}}` and `{{item}}` placeholders before running a step.
    - Dynamically expands `for_each` steps and records results as `<key>[<index>]`.
    """

    def __init__(
        self,
        provider: Provider,
        *,
        workspace: Path,
        artifact_dir: Path | None = None,
        tools: ToolRegistry | list[Tool] | None = None,
    ) -> None:
        self.provider = provider
        self.workspace = Path(workspace)
        if isinstance(tools, ToolRegistry):
            self._registry = tools
        elif isinstance(tools, list):   
            self._registry = ToolRegistry(tools, workspace=self.workspace)
        else:
            self._registry = None

    def _get_tools_for_step(self, tool_names: list[str]) -> ToolRegistry | None:
        if not tool_names or not isinstance(self._registry, ToolRegistry):
            return None
        return self._registry.subset(tool_names)

    async def run(self, plan: Plan) -> PlanResult:
        if not plan.steps:
            return PlanResult(plan=plan, status="failed", error="No steps in plan")

        try:
            validate_plan(plan)
        except Exception as exc:
            return PlanResult(plan=plan, status="failed", error=str(exc))

        step_results: dict[str, str] = {}
        loop = asyncio.get_running_loop()

        def _create_step_future() -> asyncio.Future[None]:
            fut = loop.create_future()
            fut.add_done_callback(lambda f: f.exception() if not f.cancelled() else None)
            return fut

        step_futures: dict[str, asyncio.Future[None]] = {
            s.key: _create_step_future() for s in plan.steps
        }

        async def execute_step(s: PlanStep) -> None:
            # 1) Wait for all upstream dependencies
            for dep in s.depends_on:
                await step_futures[dep]

            # 2) for_each dynamic expansion
            if s.for_each is not None:
                source_raw = step_results.get(s.for_each, "")
                items = _parse_list_output(source_raw)

                async def run_item(idx: int, item: Any) -> None:
                    rendered = _render_instruction(s.instruction, step_results, item=item)
                    tools = self._get_tools_for_step(s.tools)
                    agent = Agent(self.provider, system=s.role, tools=tools)
                    res = await agent.run(rendered)
                    step_results[f"{s.key}[{idx}]"] = res.text

                await asyncio.gather(*(run_item(i, item) for i, item in enumerate(items)))
            else:
                # 3) Regular single step execution
                rendered = _render_instruction(s.instruction, step_results)
                tools = self._get_tools_for_step(s.tools)
                agent = Agent(self.provider, system=s.role, tools=tools)
                res = await agent.run(rendered)
                step_results[s.key] = res.text

        async def step_wrapper(s: PlanStep) -> None:
            try:
                await execute_step(s)
                if not step_futures[s.key].done():
                    step_futures[s.key].set_result(None)
            except Exception as exc:
                if not step_futures[s.key].done():
                    step_futures[s.key].set_exception(exc)
                raise

        tasks = [asyncio.create_task(step_wrapper(s)) for s in plan.steps]

        try:
            await asyncio.gather(*tasks)
            return PlanResult(plan=plan, status="success", step_results=step_results)
        except Exception as exc:
            for t in tasks:
                if not t.done():
                    t.cancel()
            return PlanResult(
                plan=plan,
                status="failed",
                step_results=step_results,
                error=str(exc),
            )