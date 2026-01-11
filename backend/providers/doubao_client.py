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
        if model.startswith("deepseek-v3-1") or model.startswith("deepseek-v3-2"):
            extra_body = {"thinking": {"type": "enabled"}}
        return await super().chat(model, *args, extra_body=extra_body, **kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        if model.startswith("deepseek-v3-1") or model.startswith("deepseek-v3-2"):
            extra_body = {"thinking": {"type": "enabled"}}
        async for chunk in super().stream_chat(model, *args, extra_body=extra_body, **kwargs):
            yield chunk


# Singleton instance
doubao_client = DoubaoClient()

