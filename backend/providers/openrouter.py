from .base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    id = "openrouter"
    name = "OpenRouter"
    description = "OpenRouter (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .openrouter_client import openrouter_client
        super().__init__(openrouter_client)


provider = OpenRouterProvider()

