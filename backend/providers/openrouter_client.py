from typing import Dict
from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class OpenRouterClient(OpenAICompatibleClient):
    def __init__(self):
        default_headers: Dict[str, str] = {}
        if settings.openrouter_http_referer:
            default_headers["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_x_title:
            default_headers["X-Title"] = settings.openrouter_x_title

        super().__init__(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers=default_headers or None,
        )


openrouter_client = OpenRouterClient()

