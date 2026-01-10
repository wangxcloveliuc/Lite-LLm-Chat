import httpx
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GrokClient:
    def __init__(self):
        http_client = None
        if settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        self.client = OpenAI(
            api_key=settings.grok_api_key,
            base_url=settings.grok_base_url,
            http_client=http_client,
            timeout=settings.provider_timeout,
        )

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

                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning = delta.reasoning_content
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

            content = response.choices[0].message.content or ""
            reasoning = ""
            if hasattr(response.choices[0].message, "reasoning_content"):
                reasoning = response.choices[0].message.reasoning_content or ""

            return content, reasoning
        except Exception as e:
            raise Exception(f"Grok API error: {str(e)}")

    def list_models(self) -> List[str]:
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"Error fetching Grok models: {e}")
            return []


grok_client = GrokClient()
