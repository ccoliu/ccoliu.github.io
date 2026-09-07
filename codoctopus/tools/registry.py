# ---------------------------------------------------
# Codoctopus — Tool registry
#
# The concrete class that satisfies codoctopus.agents.ToolExecutor. It knows
# nothing about the LLM — it maps a ToolCall's name to a Tool, validates the
# arguments against that tool's own schema, and runs it.
# ---------------------------------------------------

from __future__ import annotations

from pathlib import Path

from codoctopus.llm.types import ToolCall, ToolResult, ToolSpec
from codoctopus.tools.base import Tool, ToolContext


class ToolRegistry:
    """A fixed set of tools, sharing one workspace."""

    def __init__(self, tools: list[Tool], *, workspace: Path) -> None:
        by_name = {tool.name: tool for tool in tools}
        if len(by_name) != len(tools):
            raise ValueError("tool names must be unique")
        self._tools = by_name
        self._ctx = ToolContext(workspace=workspace)

    def specs(self) -> list[ToolSpec]:
        return [tool.spec() for tool in self._tools.values()]

    def subset(self, names: list[str]) -> ToolRegistry:
        """
        A new registry holding only the named tools, sharing this one's workspace.

        For a runtime that gives each Plan step its own tool list (`PlanStep.tools`)
        without handing every step every tool the plan as a whole might use.
        """
        missing = [name for name in names if name not in self._tools]
        if missing:
            raise ValueError(f"unknown tool(s): {missing}; available: {sorted(self._tools)}")
        return ToolRegistry([self._tools[name] for name in names], workspace=self._ctx.workspace)

    async def execute(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            raise ValueError(f"unknown tool '{call.name}'; available: {sorted(self._tools)}")

        # Validation errors and run() failures both propagate — the Agent's
        # own catch-all is what turns them into an is_error ToolResult, so a
        # tool (and this registry) never needs its own error-formatting logic.
        args = tool.args_schema.model_validate(call.arguments)
        result = await tool.run(args, self._ctx)
        return ToolResult(call_id=call.id, content=result)
