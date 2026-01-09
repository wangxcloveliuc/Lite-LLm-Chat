"""
Doubao (Volcengine Ark) API client (OpenAI-compatible)

This project uses the OpenAI Python SDK and configures a provider-specific base_url.
"""

from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class DoubaoClient:
    """Client for interacting with Doubao/Volcengine Ark OpenAI-compatible API"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.doubao_api_key,
            base_url=settings.doubao_base_url,
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
            if model.startswith("deepseek-v3-1") or model.startswith("deepseek-v3-2"):
                extra_body = {"thinking": {"type": "enabled"}}
            
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

                # Handle reasoning content (for inference models) — yield reasoning first so client can buffer content properly
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    reasoning = delta.reasoning_content
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"

                # Handle regular content
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
            if model.startswith("deepseek-v3-1") or model.startswith("deepseek-v3-2"):
                extra_body = {"thinking": {"type": "enabled"}}
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=extra_body,
            )

            content = response.choices[0].message.content or ""
            reasoning = ""

            # Extract reasoning content if available (for inference models)
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content or ""

            return content, reasoning
        except Exception as e:
            raise Exception(f"Doubao API error: {str(e)}")


# Singleton instance
doubao_client = DoubaoClient()
