from .base import BaseLLMProvider


class CerebrasProvider(BaseLLMProvider):
    id = "cerebras"
    name = "Cerebras"
    description = "Cerebras Inference (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .cerebras_client import cerebras_client
        super().__init__(cerebras_client)


provider = CerebrasProvider()

