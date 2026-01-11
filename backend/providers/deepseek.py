from typing import List, Dict
from .base import BaseLLMProvider


class DeepSeekProvider(BaseLLMProvider):
    id = "deepseek"
    name = "DeepSeek"
    description = "DeepSeek AI language models"
    supported = True

    def __init__(self):
        from .deepseek_client import deepseek_client
        super().__init__(deepseek_client)

    async def list_models(self) -> List[Dict[str, object]]:
        # Hardcoded for now as DeepSeek list models might return many non-chat models
        return [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "provider": "deepseek",
                "description": "DeepSeek's flagship conversational model",
            },
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek Reasoner",
                "provider": "deepseek",
                "description": "DeepSeek's advanced reasoning model",
            },
        ]


# Module-level provider instance expected by the registry
provider = DeepSeekProvider()

