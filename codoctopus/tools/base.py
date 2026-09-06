# ---------------------------------------------------
# Codoctopus — Tool interface
#
# A Tool never touches an LLM. Its `run()` is plain Python that does the
# actual work (read a file, execute a command, run a test suite) — the model
# only ever sees the string it returns. That is the whole point of a tool:
# the agent gets to act on the real world, not just talk about it.
# ---------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel

from codoctopus.llm.schema import to_strict_schema
from codoctopus.llm.types import ToolSpec


@dataclass(frozen=True)
class ToolContext:
    """Shared resources a tool's `run()` may need. Grows as new tools need more."""

    workspace: Path


class Tool(ABC):
    """
    One capability an agent can invoke.

    Subclasses set `name`, `description`, and `args_schema` (a pydantic model
    describing the call's arguments — reusing the same strict-schema renderer
    the LLM layer uses, so a tool's declared shape and its enforced shape can
    never drift apart) and implement `run()`.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    args_schema: ClassVar[type[BaseModel]]

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.name,
            description=self.description,
            input_schema=to_strict_schema(self.args_schema),
        )

    @abstractmethod
    async def run(self, args: BaseModel, ctx: ToolContext) -> str:
        """
        Do the work and return the result as a string for the model to read.

        Raise on failure (e.g. `ValueError`) rather than returning an error
        string — `ToolRegistry.execute` lets it propagate, and the Agent's own
        catch-all turns it into an `is_error` tool result. A tool's job is to
        succeed or fail clearly, not to format its own error reporting.
        """
