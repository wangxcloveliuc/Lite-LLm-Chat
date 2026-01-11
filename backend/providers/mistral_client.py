from typing import List, Dict, Optional, Tuple
from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class MistralClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__(
            api_key=settings.mistral_api_key,
            base_url=settings.mistral_base_url,
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

    async def chat(self, model: str, *args, **kwargs) -> Tuple[str, str]:
        # Mistral might return reasoning in structured content instead of reasoning_content field
        try:
            response = self.client.chat.completions.create(
                model=model,
                stream=False,
                *args, **kwargs
            )
            message_content = response.choices[0].message.content
            reasoning, text = self._extract_reasoning_and_text(message_content)
            if not text and isinstance(message_content, str):
                text = message_content
            
            # If our base reasoning extraction didn't find anything, use what we found here
            base_reasoning = self._extract_reasoning(response.choices[0].message)
            return text or "", reasoning or base_reasoning
        except Exception as e:
            raise Exception(f"Mistral API error: {str(e)}")

    async def stream_chat(self, model: str, *args, **kwargs):
        # Override to use Mistral-specific extraction
        import json
        try:
            response = self.client.chat.completions.create(
                model=model,
                stream=True,
                *args, **kwargs
            )

            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                delta_content = getattr(delta, "content", None)
                reasoning, text = self._extract_reasoning_and_text(delta_content)

                # Also check standard reasoning field
                base_reasoning = self._extract_reasoning(delta)
                final_reasoning = reasoning or base_reasoning

                if final_reasoning:
                    yield f"data: {json.dumps({'reasoning': final_reasoning})}\n\n"
                if text:
                    yield f"data: {json.dumps({'content': text})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"


mistral_client = MistralClient()

