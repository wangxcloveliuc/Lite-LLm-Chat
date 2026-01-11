from typing import List, Dict, Optional, Tuple, AsyncIterator
import abc


class LLMProvider(abc.ABC):
    id: str
    name: str
    description: str
    supported: bool = True

    @abc.abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """
        Send a chat request and return (content, reasoning).
        """
        pass

    @abc.abstractmethod
    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Send a chat request and yield SSE-formatted chunks.
        """
        pass

    @abc.abstractmethod
    async def list_models(self) -> List[Dict[str, object]]:
        """
        Return a list of supported models.
        """
        pass

    def _format_model_name(self, model_id: str) -> str:
        """
        Helper to format a model ID into a more readable name.
        """
        # Remove organization prefix if present (e.g., 'openai/gpt-4' -> 'gpt-4')
        display_id = model_id
        
        # Replace dashes and underscores with spaces and title case
        name_parts = display_id.replace("-", " ").replace("_", " ").replace("/", " ").title().split()
        return " ".join(name_parts)


class BaseLLMProvider(LLMProvider):
    """
    Base class for providers that delegate all work to a client.
    """
    def __init__(self, client):
        self.client = client

    async def chat(self, *args, **kwargs):
        return await self.client.chat(*args, **kwargs)

    async def stream_chat(self, *args, **kwargs):
        async for chunk in self.client.stream_chat(*args, **kwargs):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        # Check if client has list_models method
        if hasattr(self.client, "list_models"):
            model_ids = self.client.list_models()
        else:
            model_ids = []

        # Fallback to hardcoded models if API returns nothing or is not supported
        if not model_ids:
            model_ids = self._get_fallback_models()

        # Filter and format 
        models = []
        for mid in model_ids:
            if self._should_skip_model(mid):
                continue
            models.append({
                "id": mid,
                "name": self._format_model_name(mid),
                "provider": self.id,
                "description": self._format_model_name(mid)
            })
        return models

    def _should_skip_model(self, model_id: str) -> bool:
        """Override to filter out specific models."""
        return False

    def _get_fallback_models(self) -> List[str]:
        """Override to provide hardcoded models when API fails."""
        return []


class BaseClient(abc.ABC):
    """Base class for all provider clients."""
    pass
