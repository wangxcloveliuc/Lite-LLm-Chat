from typing import List, Optional
from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GroqClient(OpenAICompatibleClient):
    """Client for interacting with Groq OpenAI-compatible API"""

    def __init__(self):
        super().__init__(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )

    async def chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        if model == "qwen/qwen3-32b":
            extra_body["reasoning_format"] = "parsed"
        return await super().chat(model, *args, extra_body=extra_body, **kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        if model == "qwen/qwen3-32b":
            extra_body["reasoning_format"] = "parsed"
        async for chunk in super().stream_chat(model, *args, extra_body=extra_body, **kwargs):
            yield chunk


# Singleton instance
groq_client = GroqClient()

