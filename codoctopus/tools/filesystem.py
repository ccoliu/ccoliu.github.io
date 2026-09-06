# ---------------------------------------------------
# Codoctopus — Filesystem tools
#
# Reference implementation for the tool pattern: a pydantic args model, a
# workspace-boundary check, and run() doing plain Python I/O with no LLM
# involved. shell.py / testing.py / http.py follow the same shape — each
# swaps the "do the work" step and its own safety check (an allowlist and
# timeout for shell, the SSRF check Coworkify already has for http).
# ---------------------------------------------------

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from codoctopus.tools.base import Tool, ToolContext

#: Cap how much a single read can dump into the model's context.
_MAX_READ_BYTES = 200_000


def resolve_in_workspace(workspace: Path, relative: str) -> Path:
    """
    Resolve `relative` against `workspace` and refuse anything that escapes it.

    This is the check every filesystem/shell tool needs — an agent must not be
    able to use `../../etc/passwd` (or an absolute path, or a symlink) to read
    or write outside its sandbox.
    """
    workspace = workspace.resolve()
    candidate = (workspace / relative).resolve()
    if candidate != workspace and workspace not in candidate.parents:
        raise ValueError(f"path '{relative}' escapes the workspace")
    return candidate


class ReadFileArgs(BaseModel):
    path: str = Field(description="File path, relative to the workspace root")


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a text file inside the workspace."
    args_schema = ReadFileArgs

    async def run(self, args: ReadFileArgs, ctx: ToolContext) -> str:
        target = resolve_in_workspace(ctx.workspace, args.path)
        if not target.is_file():
            raise ValueError(f"no such file: {args.path}")

        data = target.read_bytes()
        if len(data) > _MAX_READ_BYTES:
            raise ValueError(
                f"{args.path} is {len(data)} bytes, over the {_MAX_READ_BYTES}-byte read limit"
            )
        return data.decode("utf-8", errors="replace")


class WriteFileArgs(BaseModel):
    path: str = Field(description="File path, relative to the workspace root")
    content: str = Field(description="Text to write")


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write text to a file inside the workspace, creating parent directories as needed."
    args_schema = WriteFileArgs

    async def run(self, args: WriteFileArgs, ctx: ToolContext) -> str:
        target = resolve_in_workspace(ctx.workspace, args.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(args.content, encoding="utf-8")
        return f"wrote {len(args.content)} characters to {args.path}"


class ListFilesArgs(BaseModel):
    path: str = Field(default=".", description="Directory to list, relative to the workspace root")


class ListFilesTool(Tool):
    name = "list_files"
    description = "List the files and directories directly inside a workspace directory."
    args_schema = ListFilesArgs

    async def run(self, args: ListFilesArgs, ctx: ToolContext) -> str:
        target = resolve_in_workspace(ctx.workspace, args.path)
        if not target.is_dir():
            raise ValueError(f"no such directory: {args.path}")

        entries = sorted(target.iterdir(), key=lambda p: p.name)
        if not entries:
            return "(empty directory)"
        return "\n".join(f"{'d' if p.is_dir() else 'f'} {p.name}" for p in entries)
