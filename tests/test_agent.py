# ---------------------------------------------------
# Codoctopus — Agent runtime tests
#
# A ScriptedProvider replays fixed Completions and a FakeToolExecutor replays
# fixed ToolResults, so these exercise the loop itself with no API key and no
# dependency on how codoctopus.tools ends up being implemented — only on the
# ToolExecutor Protocol (specs() / execute()) that codoctopus.tools.ToolRegistry
# must satisfy.
# ---------------------------------------------------

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import pytest
from pydantic import BaseModel

from codoctopus.agents import Agent, ToolTurnLimitExceeded
from codoctopus.llm import Completion, Provider, StopReason, ToolCall, ToolResult, ToolSpec, Usage


class Plan(BaseModel):
    summary: str


class ScriptedProvider(Provider):
    """Replays a fixed sequence of Completions, recording each call it received."""

    name = "scripted"
    default_model = "scripted-1"

    def __init__(
        self,
        model: str | None = None,
        *,
        completions: list[Completion] | None = None,
        structured: bool = False,
        **options: Any,
    ) -> None:
        super().__init__(model, **options)
        self._completions = list(completions or [])
        self._structured = structured
        self.calls: list[dict[str, Any]] = []

    @property
    def supports_structured_output(self) -> bool:
        return self._structured

    async def _complete(self, messages, *, system, tools, output_schema, max_tokens, **kwargs) -> Completion:
        self.calls.append({"messages": list(messages), "system": system, "tools": tools, "schema": output_schema})
        if not self._completions:
            raise AssertionError("ScriptedProvider ran out of scripted completions")
        return self._completions.pop(0)


@dataclass
class FakeToolExecutor:
    """A minimal stand-in for codoctopus.tools.ToolRegistry."""

    tool_specs: list[ToolSpec]
    handler: Callable[[ToolCall], ToolResult | Awaitable[ToolResult]]
    calls: list[ToolCall] = field(default_factory=list)

    def specs(self) -> list[ToolSpec]:
        return self.tool_specs

    async def execute(self, call: ToolCall) -> ToolResult:
        self.calls.append(call)
        result = self.handler(call)
        if inspect.isawaitable(result):
            result = await result
        return result


READ_FILE_SPEC = ToolSpec(name="read_file", description="Read a file", input_schema={"type": "object"})


def text_completion(text: str, **kwargs: Any) -> Completion:
    return Completion(text=text, model="scripted-1", stop_reason=StopReason.END_TURN, **kwargs)


def tool_call_completion(*calls: ToolCall, **kwargs: Any) -> Completion:
    return Completion(text="", model="scripted-1", stop_reason=StopReason.TOOL_USE, tool_calls=list(calls), **kwargs)


# --- the base case ------------------------------------------------------


async def test_agent_returns_immediately_when_no_tool_is_needed():
    provider = ScriptedProvider(completions=[text_completion("done", usage=Usage(input_tokens=10, output_tokens=5))])
    agent = Agent(provider, system="be helpful")

    result = await agent.run("say hi")

    assert result.text == "done"
    assert result.turns == 1
    assert result.usage.input_tokens == 10
    assert provider.calls[0]["system"] == "be helpful"
    assert provider.calls[0]["tools"] is None, "no executor means no tools are advertised"


# --- the actual point of an Agent: tools get run and fed back -----------


async def test_agent_executes_a_tool_and_feeds_the_result_back():
    call = ToolCall(id="call_1", name="read_file", arguments={"path": "a.py"})
    provider = ScriptedProvider(
        completions=[
            tool_call_completion(call),
            text_completion("the file says hello"),
        ]
    )
    tools = FakeToolExecutor(
        tool_specs=[READ_FILE_SPEC], handler=lambda c: ToolResult(call_id=c.id, content="print('hello')")
    )
    agent = Agent(provider, tools=tools)

    result = await agent.run("what does a.py print?")

    assert result.text == "the file says hello"
    assert result.turns == 2
    assert tools.calls == [call]

    second_request = provider.calls[1]["messages"]
    assert second_request[-1].tool_results[0].content == "print('hello')"
    assert second_request[-1].tool_results[0].call_id == "call_1"


async def test_parallel_tool_calls_are_all_executed_and_returned_together():
    calls = [
        ToolCall(id="call_1", name="read_file", arguments={"path": "a.py"}),
        ToolCall(id="call_2", name="read_file", arguments={"path": "b.py"}),
    ]
    provider = ScriptedProvider(completions=[tool_call_completion(*calls), text_completion("both read")])
    tools = FakeToolExecutor(
        tool_specs=[READ_FILE_SPEC],
        handler=lambda c: ToolResult(call_id=c.id, content=f"contents of {c.arguments['path']}"),
    )
    agent = Agent(provider, tools=tools)

    await agent.run("read both files")

    assert {c.id for c in tools.calls} == {"call_1", "call_2"}
    results_message = provider.calls[1]["messages"][-1]
    assert [r.call_id for r in results_message.tool_results] == ["call_1", "call_2"], (
        "results must stay in call order even though execution is concurrent"
    )


# --- failure handling: a bad tool must not crash the loop ---------------


async def test_a_raising_tool_becomes_an_error_result_not_a_crash():
    def boom(_: ToolCall) -> ToolResult:
        raise ValueError("disk on fire")

    call = ToolCall(id="call_1", name="read_file", arguments={"path": "a.py"})
    provider = ScriptedProvider(
        completions=[tool_call_completion(call), text_completion("recovered")]
    )
    tools = FakeToolExecutor(tool_specs=[READ_FILE_SPEC], handler=boom)
    agent = Agent(provider, tools=tools)

    result = await agent.run("read a.py")

    assert result.text == "recovered", "the loop must continue past a tool failure"
    error_result = provider.calls[1]["messages"][-1].tool_results[0]
    assert error_result.is_error is True
    assert "disk on fire" in error_result.content


async def test_a_tool_call_with_no_executor_configured_is_reported_as_an_error():
    call = ToolCall(id="call_1", name="read_file", arguments={})
    provider = ScriptedProvider(completions=[tool_call_completion(call), text_completion("ok")])
    agent = Agent(provider, tools=None)

    result = await agent.run("go")

    assert result.text == "ok"
    error_result = provider.calls[1]["messages"][-1].tool_results[0]
    assert error_result.is_error is True
    assert "no tools are available" in error_result.content


# --- the runaway-loop guard ----------------------------------------------


async def test_tool_turn_limit_stops_an_agent_that_never_finishes():
    endless_call = ToolCall(id="call_1", name="read_file", arguments={})
    provider = ScriptedProvider(completions=[tool_call_completion(endless_call) for _ in range(5)])
    tools = FakeToolExecutor(tool_specs=[READ_FILE_SPEC], handler=lambda c: ToolResult(call_id=c.id, content="..."))
    agent = Agent(provider, tools=tools, max_tool_turns=3)

    with pytest.raises(ToolTurnLimitExceeded) as excinfo:
        await agent.run("loop forever")

    assert excinfo.value.max_tool_turns == 3
    assert len(tools.calls) == 3, "must stop exactly at the limit, not run past it"


# --- usage accounting and structured output pass-through -----------------


async def test_usage_accumulates_across_every_turn():
    call = ToolCall(id="call_1", name="read_file", arguments={})
    provider = ScriptedProvider(
        completions=[
            tool_call_completion(call, usage=Usage(input_tokens=100, output_tokens=20)),
            text_completion("done", usage=Usage(input_tokens=150, output_tokens=10)),
        ]
    )
    tools = FakeToolExecutor(tool_specs=[READ_FILE_SPEC], handler=lambda c: ToolResult(call_id=c.id, content="x"))
    agent = Agent(provider, tools=tools)

    result = await agent.run("go")

    assert result.usage.input_tokens == 250
    assert result.usage.output_tokens == 30


async def test_output_schema_is_forwarded_on_every_turn():
    parsed = Plan(summary="ship it")
    provider = ScriptedProvider(completions=[text_completion("{}", parsed=parsed)], structured=True)
    agent = Agent(provider, output_schema=Plan)

    result = await agent.run("plan it")

    assert result.parsed == parsed
    assert provider.calls[0]["schema"] is Plan
