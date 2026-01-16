from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class NvidiaClient(OpenAICompatibleClient):
    """Client for interacting with Nvidia NIM API"""

    def __init__(self):
        super().__init__(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )


# Singleton instance
nvidia_client = NvidiaClient()
