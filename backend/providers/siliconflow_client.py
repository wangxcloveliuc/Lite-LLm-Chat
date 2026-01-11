from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class SiliconFlowClient(OpenAICompatibleClient):
    """Client for interacting with SiliconFlow OpenAI-compatible API"""

    # Models that support thinking/reasoning capabilities
    THINKING_MODELS = {
        "zai-org/GLM-4.6",
        "Qwen/Qwen3-8B",
        "Qwen/Qwen3-14B", 
        "Qwen/Qwen3-32B",
        "wen/Qwen3-30B-A3B",
        "Qwen/Qwen3-235B-A22B",
        "tencent/Hunyuan-A13B-Instruct",
        "zai-org/GLM-4.5V",
        "deepseek-ai/DeepSeek-V3.1-Terminus",
        "Pro/deepseek-ai/DeepSeek-V3.1-Terminus",
        "deepseek-ai/DeepSeek-V3.2",
        "Pro/deepseek-ai/DeepSeek-V3.2"
    }

    def __init__(self):
        super().__init__(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )

    async def chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        if model in self.THINKING_MODELS:
            extra_body["enable_thinking"] = True
        return await super().chat(model, *args, extra_body=extra_body, **kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        extra_body = kwargs.pop("extra_body", {})
        if model in self.THINKING_MODELS:
            extra_body["enable_thinking"] = True
        async for chunk in super().stream_chat(model, *args, extra_body=extra_body, **kwargs):
            yield chunk


# Singleton instance
siliconflow_client = SiliconFlowClient()

