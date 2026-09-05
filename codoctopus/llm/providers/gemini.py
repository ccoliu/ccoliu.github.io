# ---------------------------------------------------
# Codoctopus — Google Gemini adapter
#
# Carries over the provider the `refactor` branch had hard-wired, now behind
# the same interface as every other one.
# ---------------------------------------------------

from __future__ import annotations

import json
import uuid
from typing import Any

from pydantic import BaseModel

from codoctopus.llm.base import Provider, ProviderNotInstalled
from codoctopus.llm.schema import to_strict_schema
from codoctopus.llm.types import Completion, Message, StopReason, ToolCall, ToolSpec, Usage

_STOP_REASONS = {
    "STOP": StopReason.END_TURN,
    "MAX_TOKENS": StopReason.MAX_TOKENS,
    "SAFETY": StopReason.REFUSAL,
    "PROHIBITED_CONTENT": StopReason.REFUSAL,
}


class GeminiProvider(Provider):
    name = "gemini"
    default_model = "gemini-2.0-flash"

    def __init__(self, model: str | None = None, *, api_key: str | None = None, **options: Any) -> None:
        super().__init__(model, **options)
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError as exc:  # pragma: no cover - depends on install extras
            raise ProviderNotInstalled(self.name, "google-genai") from exc
        self._types = genai_types
        self._client = genai.Client(api_key=api_key) if api_key else genai.Client()

    @property
    def supports_structured_output(self) -> bool:
        return True

    async def _complete(
        self,
        messages: list[Message],
        *,
        system: str | None,
        tools: list[ToolSpec] | None,
        output_schema: type[BaseModel] | None,
        max_tokens: int,
        **kwargs: Any,
    ) -> Completion:
        types = self._types

        config: dict[str, Any] = {"max_output_tokens": max_tokens}
        if system:
            config["system_instruction"] = system
        if tools:
            config["tools"] = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=t.name, description=t.description, parameters=t.input_schema
                        )
                        for t in tools
                    ]
                )
            ]
        if output_schema is not None:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = to_strict_schema(output_schema)
        config.update(kwargs)

        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=[_to_gemini(m, types) for m in messages],
            config=types.GenerateContentConfig(**config),
        )

        text = response.text or ""
        tool_calls = [
            ToolCall(id=f"call_{uuid.uuid4().hex[:12]}", name=c.name, arguments=dict(c.args or {}))
            for c in (response.function_calls or [])
        ]

        parsed = output_schema.model_validate(json.loads(text)) if output_schema and text else None
        candidate = (response.candidates or [None])[0]
        usage = response.usage_metadata
        return Completion(
            text=text,
            model=self.model,
            stop_reason=_STOP_REASONS.get(
                str(getattr(candidate, "finish_reason", "")).rsplit(".", 1)[-1], StopReason.OTHER
            )
            if not tool_calls
            else StopReason.TOOL_USE,
            tool_calls=tool_calls,
            parsed=parsed,
            usage=Usage(
                input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
                output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
                cache_read_tokens=getattr(usage, "cached_content_token_count", 0) or 0,
            ),
            raw=response,
        )


def _to_gemini(message: Message, types: Any) -> Any:
    """Gemini calls the assistant role "model" and wraps results in function responses."""
    if message.tool_results:
        return types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name=r.call_id, response={"error" if r.is_error else "output": r.content}
                )
                for r in message.tool_results
            ],
        )

    parts: list[Any] = []
    if message.content:
        parts.append(types.Part.from_text(text=message.content))
    parts.extend(
        types.Part.from_function_call(name=c.name, args=c.arguments) for c in message.tool_calls
    )
    return types.Content(role="model" if message.role == "assistant" else "user", parts=parts)
