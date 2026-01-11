from typing import List, Dict, AsyncIterator, Optional, Tuple
import json
from google import genai
from google.genai import types

from .base import BaseClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GeminiClient(BaseClient):
    # Models that should include thinking_config
    _THINKING_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-pro-latest",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-image-preview",
        "gemini-2.5-flash-image",
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite-preview-09-2025",
        "gemini-3-pro-preview",
        "gemini-3-flash-preview",
        "gemini-3-pro-image-preview",
        "nano-banana-pro-preview",
        "gemini-2.5-computer-use-preview-10-2025",
        "deep-research-pro-preview-12-2025",
    ]

    def __init__(self):
        http_options = None
        if settings.http_proxy:
            http_options = types.HttpOptions(
                client_args={"proxy": settings.http_proxy},
                async_client_args={"proxy": settings.http_proxy},
                timeout=settings.provider_timeout * 1000 if settings.provider_timeout else None,
            )

        self._types = types
        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=http_options,
        )

    def _should_enable_thinking(self, model: str) -> bool:
        return any(model.startswith(prefix) for prefix in self._THINKING_MODELS)


    def _messages_to_contents_and_system(self, messages: List[Dict[str, str]]):
        system_parts: List[str] = []
        contents: List[Dict[str, object]] = []

        for m in messages:
            role = (m.get("role") or "").lower()
            content = m.get("content") or ""

            if role == "system":
                if content:
                    system_parts.append(content)
                continue

            # Gemini uses 'user' and 'model'
            if role == "assistant":
                g_role = "model"
            else:
                g_role = "user"

            contents.append(
                {
                    "role": g_role,
                    "parts": [{"text": content}],
                }
            )

        system_instruction = "\n".join(system_parts).strip() or None
        return contents, system_instruction

    def _extract_text_and_reasoning(self, response) -> Tuple[str, str]:
        # Extract both thinking and regular text parts from the response in a single pass
        try:
            candidates = getattr(response, "candidates", None) or []
            if not candidates:
                return "", ""

            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []

            reasoning_parts: List[str] = []
            text_parts: List[str] = []
            
            for p in parts:
                text = getattr(p, "text", None)
                if not text:
                    continue
                    
                has_thought = getattr(p, "thought", None)
                if has_thought is True:
                    # This is a thinking part
                    reasoning_parts.append(text)
                else:
                    # This is a regular text part (thought is None, False, or missing)
                    text_parts.append(text)

            reasoning = "\n".join([x for x in reasoning_parts if x])
            content_text = "".join([x for x in text_parts if x])
            return content_text, reasoning
        except Exception as e:
            print(f"Error extracting text and reasoning: {e}")
            return "", ""

    def _extract_reasoning_from_response(self, response) -> str:
        # Backward compatibility wrapper
        _, reasoning = self._extract_text_and_reasoning(response)
        return reasoning

    def _extract_regular_text_from_response(self, response) -> str:
        # Backward compatibility wrapper
        text, _ = self._extract_text_and_reasoning(response)
        return text

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        try:
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            thinking_cfg = (
                self._types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=-1,  # Unlimited thinking budget
                )
                if enable_thinking
                else None
            )

            config = self._types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction,
                thinking_config=thinking_cfg,
            )

            # The SDK provides async streaming under client.aio
            async for chunk in await self._client.aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            ):
                reasoning = self._extract_reasoning_from_response(chunk)
                if reasoning:
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"

                # Extract only non-thinking text from the chunk
                # The chunk.text property combines all non-thinking parts
                text = self._extract_regular_text_from_response(chunk)
                if text:
                    yield f"data: {json.dumps({'content': text})}\n\n"

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
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            thinking_cfg = (
                self._types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=-1,  # Unlimited thinking budget
                )
                if enable_thinking
                else None
            )

            config = self._types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction,
                thinking_config=thinking_cfg,
            )

            response = await self._client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            content = self._extract_regular_text_from_response(response)
            reasoning = self._extract_reasoning_from_response(response)
            return content, reasoning
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def list_models(self) -> List[str]:
        try:
            model_ids: List[str] = []
            for m in self._client.models.list():
                mid = getattr(m, "name", None) or getattr(m, "id", None) or str(m)
                if isinstance(mid, str) and mid.startswith("models/"):
                    mid = mid[len("models/"):]
                if mid:
                    model_ids.append(mid)
            return model_ids
        except Exception as e:
            print(f"Error fetching Gemini models: {e}")
            return []


gemini_client = GeminiClient()
