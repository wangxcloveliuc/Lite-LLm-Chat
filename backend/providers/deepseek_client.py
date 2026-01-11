from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class DeepSeekClient(OpenAICompatibleClient):
    """Client for interacting with DeepSeek API"""

    def __init__(self):
        super().__init__(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )


# Singleton instance
deepseek_client = DeepSeekClient()

