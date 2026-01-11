from typing import List
from .base import BaseLLMProvider


class SiliconFlowProvider(BaseLLMProvider):
    id = "siliconflow"
    name = "SiliconFlow"
    description = "SiliconFlow (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .siliconflow_client import siliconflow_client
        super().__init__(siliconflow_client)

    def _get_fallback_models(self) -> List[str]:
        return [
            "Pro/THUDM/glm-4-9b-chat",
            "Pro/Qwen/Qwen2.5-7B-Instruct",
            "deepseek-ai/DeepSeek-V3",
        ]



# Module-level provider instance expected by the registry
provider = SiliconFlowProvider()
