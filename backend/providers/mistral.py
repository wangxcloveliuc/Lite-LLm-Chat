from .base import BaseLLMProvider


class MistralProvider(BaseLLMProvider):
    id = "mistral"
    name = "Mistral"
    description = "Mistral (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .mistral_client import mistral_client
        super().__init__(mistral_client)


provider = MistralProvider()

