import httpx
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class OpenRouterClient:
    def __init__(self):
        http_client = None
        if settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        default_headers: Dict[str, str] = {}
        if settings.openrouter_http_referer:
            default_headers["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_x_title:
            default_headers["X-Title"] = settings.openrouter_x_title

        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers=default_headers or None,
            http_client=http_client,
        )

    def _extract_reasoning(self, msg_or_delta) -> str:
        if msg_or_delta is None:
            return ""

        # OpenRouter normalized field
        if hasattr(msg_or_delta, "reasoning") and msg_or_delta.reasoning:
            return msg_or_delta.reasoning

        # Some providers/models may use reasoning_content
        if hasattr(msg_or_delta, "reasoning_content") and msg_or_delta.reasoning_content:
            return msg_or_delta.reasoning_content

        return ""

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in response:
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

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            msg = response.choices[0].message
            content = msg.content or ""
            reasoning = self._extract_reasoning(msg)
            return content, reasoning
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def list_models(self) -> List[str]:
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"Error fetching OpenRouter models: {e}")
            return []


openrouter_client = OpenRouterClient()
