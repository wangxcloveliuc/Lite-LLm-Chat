import httpx
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
import json

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class MistralClient:
    def __init__(self):
        http_client = None
        if settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        self.client = OpenAI(
            api_key=settings.mistral_api_key,
            base_url=settings.mistral_base_url,
            http_client=http_client,
        )

    def _extract_reasoning_and_text(self, content_obj) -> Tuple[str, str]:
        if content_obj is None:
            return "", ""

        if isinstance(content_obj, str):
            return "", content_obj

        reasoning_parts: List[str] = []
        text_parts: List[str] = []

        if isinstance(content_obj, list):
            for part in content_obj:
                if not isinstance(part, dict):
                    continue
                part_type = part.get("type")

                if part_type == "thinking":
                    thinking = part.get("thinking")
                    if isinstance(thinking, list):
                        for t in thinking:
                            if isinstance(t, dict) and t.get("type") == "text" and isinstance(t.get("text"), str):
                                reasoning_parts.append(t.get("text") or "")
                elif part_type == "text":
                    if isinstance(part.get("text"), str):
                        text_parts.append(part.get("text") or "")

        return "".join(reasoning_parts), "".join(text_parts)

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

                delta_content = getattr(delta, "content", None)
                reasoning, text = self._extract_reasoning_and_text(delta_content)

                if reasoning:
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"
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
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            message_content = response.choices[0].message.content
            reasoning, text = self._extract_reasoning_and_text(message_content)
            if not text and isinstance(message_content, str):
                text = message_content
            return text or "", reasoning or ""
        except Exception as e:
            raise Exception(f"Mistral API error: {str(e)}")

    def list_models(self) -> List[str]:
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"Error fetching Mistral models: {e}")
            return []


mistral_client = MistralClient()
