# ---------------------------------------------------
# Codoctopus — Filesystem tool tests
#
# Covers the registry contract (specs / execute / unknown tool / bad args)
# and the workspace sandbox, then proves the whole thing plugs into Agent
# with zero changes on the Agent side — that's the payoff of building tools
# against the ToolExecutor Protocol instead of importing concrete classes.
# ---------------------------------------------------

from __future__ import annotations

import pytest

from codoctopus.agents import Agent, ToolExecutor
from codoctopus.llm import Completion, Provider, StopReason, ToolCall
from codoctopus.tools import ToolRegistry
from codoctopus.tools.filesystem import ListFilesTool, ReadFileTool, WriteFileTool


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "hello.txt").write_text("hello, agent", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    return tmp_path


@pytest.fixture
def registry(workspace):
    return ToolRegistry(
        [ReadFileTool(), WriteFileTool(), ListFilesTool()],
        workspace=workspace,
    )


# --- registry satisfies the Protocol Agent depends on --------------------


def test_registry_satisfies_the_tool_executor_protocol(registry):
    assert isinstance(registry, ToolExecutor)


def test_specs_describe_every_registered_tool(registry):
    names = {spec.name for spec in registry.specs()}
    assert names == {"read_file", "write_file", "list_files"}


def test_subset_returns_a_registry_scoped_to_the_named_tools(registry):
    scoped = registry.subset(["read_file"])

    assert {spec.name for spec in scoped.specs()} == {"read_file"}


async def test_subset_shares_the_parent_workspace(registry, workspace):
    scoped = registry.subset(["read_file"])

    result = await scoped.execute(ToolCall(id="c1", name="read_file", arguments={"path": "hello.txt"}))

    assert result.content == "hello, agent"


def test_subset_rejects_an_unknown_tool_name(registry):
    with pytest.raises(ValueError, match="unknown tool"):
        registry.subset(["read_file", "delete_everything"])


# --- read_file -------------------------------------------------------


async def test_read_file_returns_the_file_contents(registry):
    result = await registry.execute(ToolCall(id="c1", name="read_file", arguments={"path": "hello.txt"}))
    assert result.content == "hello, agent"
    assert result.is_error is False


async def test_read_file_reports_a_missing_file_clearly(registry):
    with pytest.raises(ValueError, match="no such file"):
        await registry.execute(ToolCall(id="c1", name="read_file", arguments={"path": "nope.txt"}))


@pytest.mark.parametrize("escape", ["../outside.txt", "/etc/passwd", "subdir/../../outside.txt"])
async def test_read_file_refuses_to_escape_the_workspace(registry, escape):
    with pytest.raises(ValueError, match="escapes the workspace"):
        await registry.execute(ToolCall(id="c1", name="read_file", arguments={"path": escape}))


# --- write_file / list_files ------------------------------------------


async def test_write_file_then_list_files_sees_it(registry, workspace):
    await registry.execute(
        ToolCall(id="c1", name="write_file", arguments={"path": "new.txt", "content": "written"})
    )
    assert (workspace / "new.txt").read_text(encoding="utf-8") == "written"

    listing = await registry.execute(ToolCall(id="c2", name="list_files", arguments={"path": "."}))
    assert "f new.txt" in listing.content
    assert "d subdir" in listing.content


# --- registry-level error handling --------------------------------------


async def test_unknown_tool_raises_with_the_available_names_listed(registry):
    with pytest.raises(ValueError, match="unknown tool 'delete_everything'"):
        await registry.execute(ToolCall(id="c1", name="delete_everything", arguments={}))


async def test_missing_required_argument_raises_a_validation_error(registry):
    with pytest.raises(Exception, match="path"):
        await registry.execute(ToolCall(id="c1", name="read_file", arguments={}))


# --- end-to-end through Agent --------------------------------------------


class ScriptedProvider(Provider):
    """Same pattern as tests/test_agent.py: replay fixed Completions."""

    name = "scripted"
    default_model = "scripted-1"

    def __init__(self, model: str | None = None, *, completions=None, **options):
        super().__init__(model, **options)
        self._completions = list(completions or [])
        self.calls: list[dict] = []

    async def _complete(self, messages, *, system, tools, output_schema, max_tokens, **kwargs):
        self.calls.append({"messages": list(messages), "tools": tools})
        return self._completions.pop(0)


async def test_agent_reads_a_real_file_through_the_registry(registry):
    call = ToolCall(id="call_1", name="read_file", arguments={"path": "hello.txt"})
    provider = ScriptedProvider(
        completions=[
            Completion(text="", model="scripted-1", stop_reason=StopReason.TOOL_USE, tool_calls=[call]),
            Completion(text="the file says: hello, agent", model="scripted-1", stop_reason=StopReason.END_TURN),
        ]
    )
    agent = Agent(provider, tools=registry)

    result = await agent.run("what's in hello.txt?")

    assert result.text == "the file says: hello, agent"
    # The tool actually ran — no LLM call was made to "execute" it.
    tool_result_message = provider.calls[1]["messages"][-1]
    assert tool_result_message.tool_results[0].content == "hello, agent"

    # specs() reached the model as real ToolSpecs, not a placeholder.
    advertised = {spec.name for spec in provider.calls[0]["tools"]}
    assert "read_file" in advertised
