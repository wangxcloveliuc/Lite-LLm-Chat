from typing import List
from .base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    id = "groq"
    name = "Groq"
    description = "Groq (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .groq_client import groq_client
        super().__init__(groq_client)

    def _should_skip_model(self, model_id: str) -> bool:
        return "whisper" in model_id.lower()

    def _get_fallback_models(self) -> List[str]:
        return [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ]


# Module-level provider instance expected by the registry
provider = GroqProvider()

