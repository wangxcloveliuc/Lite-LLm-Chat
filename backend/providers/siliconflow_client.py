from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class SiliconFlowClient(OpenAICompatibleClient):
    """Client for interacting with SiliconFlow OpenAI-compatible API"""

    def __init__(self):
        super().__init__(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )

    async def _prepare_extra_body(self, model: str, kwargs: dict) -> dict:
        extra_body = kwargs.pop("extra_body", {})
        
        # Extract SiliconFlow specific parameters
        enable_thinking = kwargs.pop("enable_thinking", None)
        thinking_budget = kwargs.pop("thinking_budget", None)
        min_p = kwargs.pop("min_p", None)
        top_k = kwargs.pop("top_k", None)

        if enable_thinking is not None:
            extra_body["enable_thinking"] = enable_thinking

        if thinking_budget is not None:
            extra_body["thinking_budget"] = thinking_budget
        
        if min_p is not None:
            extra_body["min_p"] = min_p
            
        if top_k is not None:
            extra_body["top_k"] = top_k
            
        return extra_body

    async def chat(self, model: str, *args, **kwargs):
        extra_body = await self._prepare_extra_body(model, kwargs)
        return await super().chat(model, *args, extra_body=extra_body, **kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        extra_body = await self._prepare_extra_body(model, kwargs)
        async for chunk in super().stream_chat(model, *args, extra_body=extra_body, **kwargs):
            yield chunk


# Singleton instance
siliconflow_client = SiliconFlowClient()

