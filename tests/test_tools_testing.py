# ---------------------------------------------------
# Codoctopus — Test-running tool tests
#
# Runs real pytest subprocesses against small fixture test files written into
# tmp_path — this is the one tool where a mock would prove nothing, since the
# whole point is that it actually executes the suite.
# ---------------------------------------------------

from __future__ import annotations

import pytest

from codoctopus.tools.base import ToolContext
from codoctopus.tools.testing import RunTestsArgs, RunTestsTool


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def ctx(workspace):
    return ToolContext(workspace=workspace)


async def test_a_passing_suite_reports_passed(workspace, ctx):
    (workspace / "test_ok.py").write_text("def test_it():\n    assert 1 + 1 == 2\n")

    result = await RunTestsTool().run(RunTestsArgs(), ctx)

    assert result.startswith("PASSED")
    assert "1 passed" in result


async def test_a_failing_suite_reports_failed_with_the_assertion(workspace, ctx):
    (workspace / "test_bad.py").write_text("def test_it():\n    assert 1 + 1 == 3, 'math is broken'\n")

    result = await RunTestsTool().run(RunTestsArgs(), ctx)

    assert result.startswith("FAILED")
    assert "1 failed" in result
    assert "math is broken" in result


async def test_keyword_filter_only_runs_matching_tests(workspace, ctx):
    (workspace / "test_mixed.py").write_text(
        "def test_alpha():\n    assert True\n\n"
        "def test_beta():\n    assert False\n"
    )

    result = await RunTestsTool().run(RunTestsArgs(keyword="alpha"), ctx)

    assert result.startswith("PASSED")
    assert "1 passed" in result


async def test_path_argument_scopes_to_one_file(workspace, ctx):
    (workspace / "test_good.py").write_text("def test_it():\n    assert True\n")
    (workspace / "test_broken.py").write_text("def test_it():\n    assert False\n")

    result = await RunTestsTool().run(RunTestsArgs(path="test_good.py"), ctx)

    assert result.startswith("PASSED")
    assert "1 passed" in result


async def test_path_cannot_escape_the_workspace(workspace, ctx):
    with pytest.raises(ValueError, match="escapes the workspace"):
        await RunTestsTool().run(RunTestsArgs(path="../../etc"), ctx)


async def test_a_hanging_test_is_killed_at_the_timeout(workspace, ctx):
    (workspace / "test_slow.py").write_text(
        "import time\ndef test_it():\n    time.sleep(30)\n"
    )

    with pytest.raises(ValueError, match="timed out"):
        await RunTestsTool().run(RunTestsArgs(timeout_seconds=1), ctx)
