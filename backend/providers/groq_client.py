"""
Groq API client (OpenAI-compatible)

This project uses the OpenAI Python SDK and configures a provider-specific base_url.
"""
import httpx
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GroqClient:
    """Client for interacting with Groq OpenAI-compatible API"""

    def __init__(self):
        http_client = None
        if settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        self.client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
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
            extra_body = {}
            if model == "qwen/qwen3-32b":
                extra_body["reasoning_format"] = "parsed"

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_body=extra_body,
            )

            for chunk in response:
                delta = chunk.choices[0].delta

                if hasattr(delta, "reasoning") and delta.reasoning:
                    reasoning = delta.reasoning
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
            extra_body = {}
            if model == "qwen/qwen3-32b":
                extra_body["reasoning_format"] = "parsed"

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=extra_body
            )

            content = response.choices[0].message.content or ""
            reasoning = ""
            if hasattr(response.choices[0].message, "reasoning"):
                reasoning = response.choices[0].message.reasoning or ""

            return content, reasoning
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    def list_models(self) -> List[str]:
        """List available models from Groq API"""
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"Error fetching Groq models: {e}")
            return []


# Singleton instance
groq_client = GroqClient()
