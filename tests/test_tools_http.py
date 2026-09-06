# ---------------------------------------------------
# Codoctopus — HTTP tool tests
#
# The SSRF guard is tested directly against `_validate_public_url` (no
# network needed) plus one end-to-end request against a local httpx mock
# transport, so nothing here depends on real internet access.
# ---------------------------------------------------

from __future__ import annotations

import httpx
import pytest

from codoctopus.tools.base import ToolContext
from codoctopus.tools.http import HttpRequestArgs, HttpRequestTool, _validate_public_url


@pytest.fixture
def ctx(tmp_path):
    return ToolContext(workspace=tmp_path)


# --- SSRF guard --------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata endpoint
        "http://10.0.0.5/",
        "http://192.168.1.1/",
    ],
)
def test_validate_public_url_blocks_non_public_targets(url):
    with pytest.raises(ValueError, match="forbidden IP address"):
        _validate_public_url(url)


def test_validate_public_url_rejects_a_non_http_scheme():
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        _validate_public_url("file:///etc/passwd")


def test_validate_public_url_accepts_a_public_address():
    _validate_public_url("http://93.184.216.34/")  # a public IP literal - no DNS needed


# --- the tool itself, via a mock transport ------------------------------


def _mock_client_factory(handler):
    """
    Build a drop-in replacement for httpx.AsyncClient backed by a MockTransport.

    Captures the real AsyncClient class before it is patched — patching
    `codoctopus.tools.http.httpx.AsyncClient` replaces the attribute on the
    shared `httpx` module itself, so a lambda that calls `httpx.AsyncClient(...)`
    from inside would end up calling the very patch it's part of.
    """
    real_async_client = httpx.AsyncClient

    def factory(**kw):
        return real_async_client(transport=httpx.MockTransport(handler), **kw)

    return factory


async def test_http_request_returns_status_and_body(ctx, monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-test"] == "1"
        return httpx.Response(200, text="ok")

    monkeypatch.setattr("codoctopus.tools.http.httpx.AsyncClient", _mock_client_factory(handler))
    # Bypass the SSRF check for this fake host, which does not resolve.
    monkeypatch.setattr("codoctopus.tools.http._validate_public_url", lambda url: None)

    tool = HttpRequestTool()
    result = await tool.run(HttpRequestArgs(url="http://example.test/", headers={"x-test": "1"}), ctx)

    assert "HTTP 200" in result
    assert "ok" in result


async def test_http_request_truncates_a_huge_response(ctx, monkeypatch):
    huge = "x" * 30_000

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=huge)

    monkeypatch.setattr("codoctopus.tools.http.httpx.AsyncClient", _mock_client_factory(handler))
    monkeypatch.setattr("codoctopus.tools.http._validate_public_url", lambda url: None)

    tool = HttpRequestTool()
    result = await tool.run(HttpRequestArgs(url="http://example.test/"), ctx)

    assert "truncated" in result
    assert len(result) < len(huge)


async def test_http_request_refuses_a_private_target_before_any_network_call(ctx):
    tool = HttpRequestTool()
    with pytest.raises(ValueError, match="forbidden IP address"):
        await tool.run(HttpRequestArgs(url="http://127.0.0.1/admin"), ctx)
