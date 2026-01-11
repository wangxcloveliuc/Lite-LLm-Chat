from .base import BaseLLMProvider


class GrokProvider(BaseLLMProvider):
    id = "grok"
    name = "Grok"
    description = "Grok (xAI, OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .grok_client import grok_client
        super().__init__(grok_client)


provider = GrokProvider()

