"""
DeepSeek API client (moved into providers)
"""
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json
try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class DeepSeekClient:
    """Client for interacting with DeepSeek API"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=settings.provider_timeout,
        )

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: int = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from DeepSeek
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in response:
                delta = chunk.choices[0].delta

                # Handle reasoning content (for inference models) — yield reasoning first so client can buffer content properly
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    reasoning = delta.reasoning_content
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"

                # Handle regular content
                if delta.content:
                    content = delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: int = None
    ) -> tuple[str, str]:
        """
        Non-streaming chat completion
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            content = response.choices[0].message.content or ""
            reasoning = ""

            # Extract reasoning content if available (for inference models)
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content or ""

            return content, reasoning
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")


# Singleton instance
deepseek_client = DeepSeekClient()
