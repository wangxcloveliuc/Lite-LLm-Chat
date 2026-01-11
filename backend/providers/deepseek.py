from typing import List
from .base import BaseLLMProvider


class DeepSeekProvider(BaseLLMProvider):
    id = "deepseek"
    name = "DeepSeek"
    description = "DeepSeek AI language models"
    supported = True

    def __init__(self):
        from .deepseek_client import deepseek_client
        super().__init__(deepseek_client)

    def _get_fallback_models(self) -> List[str]:
        return [
            "deepseek-chat",
            "deepseek-reasoner",
        ]


# Module-level provider instance expected by the registry
provider = DeepSeekProvider()

