from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class CerebrasClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )


cerebras_client = CerebrasClient()

