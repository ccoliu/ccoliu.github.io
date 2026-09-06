# ---------------------------------------------------
# Codoctopus — Test-running tool
#
# This is what makes v1's "automated verification layer" real: v1's verifier
# was another LLM call looking at code and guessing whether it had problems.
# This one actually runs the test suite and reports what happened.
# ---------------------------------------------------

from __future__ import annotations

import asyncio
import sys

from pydantic import BaseModel, Field

from codoctopus.tools.base import Tool, ToolContext
from codoctopus.tools.filesystem import resolve_in_workspace

#: Cap how much of pytest's output reaches the model's context.
_MAX_OUTPUT_CHARS = 20_000


class RunTestsArgs(BaseModel):
    path: str = Field(default=".", description="Test file or directory, relative to the workspace root")
    keyword: str | None = Field(default=None, description="Only run tests matching this pytest -k expression")
    timeout_seconds: float = Field(default=120.0, gt=0, le=600, description="Timeout for the whole run, capped at 600s")


class RunTestsTool(Tool):
    """Run the workspace's pytest suite and report the result."""

    name = "run_tests"
    description = "Run the project's pytest suite inside the workspace and report pass/fail results."
    args_schema = RunTestsArgs

    async def run(self, args: RunTestsArgs, ctx: ToolContext) -> str:
        target = resolve_in_workspace(ctx.workspace, args.path)

        # Invoke via `sys.executable -m pytest` rather than a bare `pytest` on
        # PATH, so this always runs in the same interpreter as Codoctopus itself.
        command = [sys.executable, "-m", "pytest", str(target), "-q", "--tb=short", "--color=no"]
        if args.keyword:
            command += ["-k", args.keyword]

        proc = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(ctx.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            output_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=args.timeout_seconds)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise ValueError(f"Test run timed out after {args.timeout_seconds}s")

        output = output_bytes.decode("utf-8", errors="replace")
        if len(output) > _MAX_OUTPUT_CHARS:
            # Keep the tail: pytest's pass/fail summary and short tracebacks
            # land at the end of the output, not the collection noise at the start.
            output = "...[truncated]...\n" + output[-_MAX_OUTPUT_CHARS:]

        status = "PASSED" if proc.returncode == 0 else "FAILED"
        return f"{status} (exit code {proc.returncode})\n\n{output}"
