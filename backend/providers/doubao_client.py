import base64
import json
import mimetypes
import os
from typing import AsyncIterator, Dict, List, Optional, Tuple

from volcenginesdkarkruntime import Ark

from .base import BaseClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class DoubaoClient(BaseClient):
    """Client for interacting with Doubao/Volcengine Ark native SDK."""

    def __init__(self):
        # Ark SDK uses api_key; base_url is optional (defaults to CN-Beijing endpoint).
        self.client = Ark(
            api_key=settings.doubao_api_key,
            base_url=getattr(settings, "doubao_base_url", None),
        )

    def _extract_reasoning(self, msg_or_delta) -> str:
        """Extract reasoning/thinking content from message or delta."""
        if msg_or_delta is None:
            return ""
        for field in ["reasoning_content", "reasoning", "thought"]:
            if hasattr(msg_or_delta, field):
                val = getattr(msg_or_delta, field)
                if val:
                    return val
        return ""

    def _process_messages(
        self,
        messages: List[Dict],
        image_detail: Optional[str] = None,
        image_pixel_limit: Optional[Dict] = None,
    ) -> List[Dict]:
        """Convert local image URLs to data URIs for Ark vision support."""
        new_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if isinstance(content, list):
                new_parts = []
                for part in content:
                    if part.get("type") == "image_url" and "image_url" in part:
                        url = part["image_url"].get("url", "")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "image/jpeg"
                                    with open(local_path, "rb") as image_file:
                                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                                        new_part = part.copy()
                                        new_part["image_url"] = {"url": f"data:{mime_type};base64,{base64_image}"}
                                        if image_detail:
                                            new_part["image_url"]["detail"] = image_detail
                                        if image_pixel_limit:
                                            new_part["image_url"]["image_pixel_limit"] = image_pixel_limit
                                        new_parts.append(new_part)
                                        continue
                                else:
                                    print(f"[DoubaoArk] Image not found: {local_path}")
                            except Exception as e:
                                print(f"[DoubaoArk] Error processing image {url}: {e}")
                    new_parts.append(part)
                new_messages.append({"role": role, "content": new_parts})
            else:
                new_messages.append(msg)
        return new_messages

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        try:
            extra_body = kwargs.pop("extra_body", {}) or {}
            thinking = kwargs.pop("thinking", None)
            reasoning_effort = kwargs.pop("reasoning_effort", None)
            max_completion_tokens = kwargs.pop("max_completion_tokens", None)
            image_detail = kwargs.pop("image_detail", None)
            image_pixel_limit = kwargs.pop("image_pixel_limit", None)

            if thinking is True:
                extra_body["thinking"] = {"type": "enabled"}
            elif thinking is False:
                extra_body["thinking"] = {"type": "disabled"}

            if reasoning_effort:
                extra_body["reasoning_effort"] = reasoning_effort

            if max_completion_tokens is not None:
                kwargs["max_completion_tokens"] = max_completion_tokens

            processed_messages = self._process_messages(
                messages, image_detail=image_detail, image_pixel_limit=image_pixel_limit
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=extra_body,
                **kwargs,
            )

            msg = response.choices[0].message
            content = getattr(msg, "content", "") or ""
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
        **kwargs,
    ) -> AsyncIterator[str]:
        try:
            extra_body = kwargs.pop("extra_body", {}) or {}
            thinking = kwargs.pop("thinking", None)
            reasoning_effort = kwargs.pop("reasoning_effort", None)
            max_completion_tokens = kwargs.pop("max_completion_tokens", None)
            image_detail = kwargs.pop("image_detail", None)
            image_pixel_limit = kwargs.pop("image_pixel_limit", None)

            if thinking is True:
                extra_body["thinking"] = {"type": "enabled"}
            elif thinking is False:
                extra_body["thinking"] = {"type": "disabled"}

            if reasoning_effort:
                extra_body["reasoning_effort"] = reasoning_effort

            if max_completion_tokens is not None:
                kwargs["max_completion_tokens"] = max_completion_tokens

            processed_messages = self._process_messages(
                messages, image_detail=image_detail, image_pixel_limit=image_pixel_limit
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_body=extra_body,
                **kwargs,
            )

            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                reasoning = self._extract_reasoning(delta)
                if reasoning:
                    yield f"data: {json.dumps({'reasoning': reasoning})}\n\n"

                if getattr(delta, "content", None):
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"


# Singleton instance
doubao_client = DoubaoClient()

