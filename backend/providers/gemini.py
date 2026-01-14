from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    id = "gemini"
    name = "Gemini"
    description = "Google Gemini (google-genai SDK) models"
    supported = True

    def __init__(self):
        from .gemini_client import gemini_client
        super().__init__(gemini_client)


provider = GeminiProvider()

