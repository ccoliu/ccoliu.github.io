# ---------------------------------------------------
# Codoctopus — Domain base and registry tests
# ---------------------------------------------------

from __future__ import annotations

import pytest

from codoctopus.domains import Domain, get_domain, register_domain
from codoctopus.domains.base import VerifyResult
from codoctopus.tools.base import ToolContext


class MinimalDomain(Domain):
    """A domain that overrides nothing but `name` — proves the base defaults hold."""

    name = "minimal"


# --- base class defaults -------------------------------------------------


async def test_a_domain_with_no_roles_or_tools_still_works(tmp_path):
    domain = MinimalDomain()

    assert domain.roles == {}
    assert domain.default_tools == []
    assert domain.planner_hint == ""

    result = await domain.verify(step_results={}, ctx=ToolContext(workspace=tmp_path))
    assert isinstance(result, VerifyResult)
    assert result.passed is True


# --- registry --------------------------------------------------------


def test_a_custom_domain_resolves_through_the_registry():
    register_domain("minimal", MinimalDomain)

    domain = get_domain("minimal")

    assert isinstance(domain, MinimalDomain)
    assert domain.name == "minimal"


def test_unknown_domain_lists_what_is_available():
    with pytest.raises(ValueError, match="Unknown domain 'nope'"):
        get_domain("nope")
