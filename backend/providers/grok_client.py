from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GrokClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__(
            api_key=settings.grok_api_key,
            base_url=settings.grok_base_url,
        )


grok_client = GrokClient()

