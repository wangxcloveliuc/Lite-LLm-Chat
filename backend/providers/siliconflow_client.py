"""
SiliconFlow API client (OpenAI-compatible)

This project uses the OpenAI Python SDK and configures a provider-specific base_url.
"""

from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class SiliconFlowClient:
    """Client for interacting with SiliconFlow OpenAI-compatible API"""

    # Models that support thinking/reasoning capabilities
    THINKING_MODELS = {
        "zai-org/GLM-4.6",
        "Qwen/Qwen3-8B",
        "Qwen/Qwen3-14B", 
        "Qwen/Qwen3-32B",
        "wen/Qwen3-30B-A3B",
        "Qwen/Qwen3-235B-A22B",
        "tencent/Hunyuan-A13B-Instruct",
        "zai-org/GLM-4.5V",
        "deepseek-ai/DeepSeek-V3.1-Terminus",
        "Pro/deepseek-ai/DeepSeek-V3.1-Terminus",
        "deepseek-ai/DeepSeek-V3.2",
        "Pro/deepseek-ai/DeepSeek-V3.2"
    }

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
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
            # Only enable thinking for specific models
            extra_body = {"enable_thinking": True} if model in self.THINKING_MODELS else None
            
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
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
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
            # Only enable thinking for specific models
            extra_body = {"enable_thinking": True} if model in self.THINKING_MODELS else None
            
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
            if hasattr(response.choices[0].message, "reasoning_content"):
                reasoning = response.choices[0].message.reasoning_content or ""

            return content, reasoning
        except Exception as e:
            raise Exception(f"SiliconFlow API error: {str(e)}")


# Singleton instance
siliconflow_client = SiliconFlowClient()
