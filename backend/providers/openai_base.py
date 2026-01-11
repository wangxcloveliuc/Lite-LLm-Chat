import json
import httpx
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
from .base import BaseClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class OpenAICompatibleClient(BaseClient):
    """Base client for all OpenAI-compatible providers."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        use_proxy: bool = True
    ):
        http_client = None
        if use_proxy and settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers,
            http_client=http_client,
            timeout=settings.provider_timeout,
        )

    def _extract_reasoning(self, msg_or_delta) -> str:
        """Extract reasoning content from message or delta."""
        if msg_or_delta is None:
            return ""

        # Check common fields across different providers
        for field in ["reasoning_content", "reasoning", "thought"]:
            if hasattr(msg_or_delta, field):
                val = getattr(msg_or_delta, field)
                if val:
                    return val
        
        return ""

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        extra_body: Optional[Dict] = None,
    ) -> Tuple[str, str]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=extra_body,
            )

            msg = response.choices[0].message
            content = msg.content or ""
            reasoning = self._extract_reasoning(msg)
            return content, reasoning
        except Exception as e:
            raise Exception(f"API error: {str(e)}")

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        extra_body: Optional[Dict] = None,
    ) -> AsyncIterator[str]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_body=extra_body,
            )

            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                reasoning = self._extract_reasoning(delta)
                if reasoning:
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"

                if getattr(delta, "content", None):
                    content = delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    def list_models(self) -> List[str]:
        """Fetch models from the provider's API."""
        try:
            # Not all OpenAI-compatible providers allow listing models
            response = self.client.models.list()
            return [m.id for m in response.data]
        except Exception:
            return []
