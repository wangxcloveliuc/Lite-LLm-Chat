from typing import List
from .base import BaseLLMProvider


class NvidiaProvider(BaseLLMProvider):
    id = "nvidia"
    name = "Nvidia"
    description = "Nvidia NIM language models"
    supported = True

    def __init__(self):
        from .nvidia_client import nvidia_client
        super().__init__(nvidia_client)

    def _get_fallback_models(self) -> List[str]:
        return [
            "nvidia/llama-3.1-8b-instruct",
            "nvidia/llama-3.1-70b-instruct",
            "nvidia/llama-3.1-405b-instruct",
        ]


# Module-level provider instance expected by the registry
provider = NvidiaProvider()
