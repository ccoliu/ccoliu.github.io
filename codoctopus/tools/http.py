# ---------------------------------------------------
# Codoctopus — HTTP tool
#
# `_validate_public_url` is shared: codoctopus.tools.shell imports it directly
# to guard curl invocations against the same targets. Keep the two call sites
# in sync if this check changes.
# ---------------------------------------------------

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

from codoctopus.tools.base import Tool, ToolContext

#: Cap how much of a response body reaches the model's context.
_MAX_RESPONSE_CHARS = 20_000


def _validate_public_url(url: str) -> None:
    """
    Refuse a URL whose host resolves to a private, loopback, link-local,
    reserved, or multicast address — the standard SSRF guard against an agent
    being tricked into hitting internal services or a cloud metadata endpoint.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme!r}")

    hostname = parsed.hostname
    if hostname is None:
        raise ValueError(f"Invalid URL: {url}")

    try:
        resolved = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Failed to resolve hostname: {hostname}") from exc

    for info in resolved:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"Hostname resolved to a forbidden IP address: {ip}")


class HttpRequestArgs(BaseModel):
    url: str = Field(description="URL to request. Must be a public http:// or https:// address.")
    method: str = Field(default="GET", description="HTTP method, e.g. GET, POST, PUT, DELETE")
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers")
    body: str | None = Field(
        default=None,
        description="Raw request body. To send JSON, put the JSON text here and set "
        "a Content-Type: application/json header.",
    )
    timeout_seconds: float = Field(default=10.0, gt=0, le=30, description="Request timeout, capped at 30s")


class HttpRequestTool(Tool):
    """
    Make an outbound HTTP request.

    Redirects are never followed automatically — a redirect response is
    returned as-is so the caller can see where it points without this tool
    silently walking a chain of untrusted, unvalidated hops.
    """

    name = "http_request"
    description = (
        "Make an HTTP request to a public URL. Cannot reach private networks, "
        "localhost, or cloud metadata endpoints."
    )
    args_schema = HttpRequestArgs

    async def run(self, args: HttpRequestArgs, ctx: ToolContext) -> str:
        _validate_public_url(args.url)

        async with httpx.AsyncClient(follow_redirects=False, timeout=args.timeout_seconds) as client:
            try:
                response = await client.request(
                    args.method.upper(),
                    args.url,
                    headers=args.headers,
                    content=args.body,
                )
            except httpx.HTTPError as exc:
                raise ValueError(f"Request failed: {exc}") from exc

        body = response.text
        truncated = len(body) > _MAX_RESPONSE_CHARS
        summary = f"HTTP {response.status_code}\n\n{body[:_MAX_RESPONSE_CHARS]}"
        if truncated:
            summary += f"\n\n[response truncated to {_MAX_RESPONSE_CHARS} characters]"
        return summary
