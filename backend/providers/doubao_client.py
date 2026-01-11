from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class DoubaoClient(OpenAICompatibleClient):
    """Client for interacting with Doubao/Volcengine Ark OpenAI-compatible API"""

    def __init__(self):
        super().__init__(
            api_key=settings.doubao_api_key,
            base_url=settings.doubao_base_url,
        )

    async def chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        thinking = kwargs.pop("thinking", None)
        reasoning_effort = kwargs.pop("reasoning_effort", None)
        max_completion_tokens = kwargs.pop("max_completion_tokens", None)

        if thinking is True:
            extra_body["thinking"] = {"type": "enabled"}
        elif thinking is False:
            extra_body["thinking"] = {"type": "disabled"}
        
        if reasoning_effort:
            extra_body["reasoning_effort"] = reasoning_effort
        
        if max_completion_tokens is not None:
            kwargs["max_completion_tokens"] = max_completion_tokens

        return await super().chat(model, *args, extra_body=extra_body, **kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        thinking = kwargs.pop("thinking", None)
        reasoning_effort = kwargs.pop("reasoning_effort", None)
        max_completion_tokens = kwargs.pop("max_completion_tokens", None)

        if thinking is True:
            extra_body["thinking"] = {"type": "enabled"}
        elif thinking is False:
            extra_body["thinking"] = {"type": "disabled"}
            
        if reasoning_effort:
            extra_body["reasoning_effort"] = reasoning_effort
            
        if max_completion_tokens is not None:
            kwargs["max_completion_tokens"] = max_completion_tokens

        async for chunk in super().stream_chat(model, *args, extra_body=extra_body, **kwargs):
            yield chunk


# Singleton instance
doubao_client = DoubaoClient()

