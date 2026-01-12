import json
import httpx
import base64
import os
import mimetypes
from openai import OpenAI
from typing import List, Dict, AsyncIterator, Optional, Tuple
from .base import BaseClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class OpenAICompatibleClient(BaseClient):
    """Base client for all OpenAI-compatible providers."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        use_proxy: bool = True
    ):
        http_client = None
        if use_proxy and settings.http_proxy:
            http_client = httpx.Client(
                proxy=settings.http_proxy,
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers,
            http_client=http_client,
            timeout=settings.provider_timeout,
        )

    def _extract_reasoning(self, msg_or_delta) -> str:
        """Extract reasoning content from message or delta."""
        if msg_or_delta is None:
            return ""

        # Check common fields across different providers
        for field in ["reasoning_content", "reasoning", "thought"]:
            if hasattr(msg_or_delta, field):
                val = getattr(msg_or_delta, field)
                if val:
                    return val
        
        return ""

    def _process_messages(self, messages: List[Dict]) -> List[Dict]:
        """Process messages to convert local image URLs to data URIs."""
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
                            # Resolve local path
                            try:
                                # Start from the directory where this file resides
                                # providers/ -> backend/
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                
                                # Remove leading slash and join
                                # e.g. "uploads/xxx.jpg"
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)
                                
                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "image/jpeg"
                                    with open(local_path, "rb") as image_file:
                                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                                        # Update the part with data URI
                                        new_part = part.copy()
                                        new_part["image_url"] = {"url": f"data:{mime_type};base64,{base64_image}"}
                                        new_parts.append(new_part)
                                        continue
                                else:
                                    print(f"[OpenAIClient] Image not found: {local_path}")
                            except Exception as e:
                                print(f"[OpenAIClient] Error processing image {url}: {e}")
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
        extra_body: Optional[Dict] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        try:
            # Clean up kwargs
            sanitized_kwargs = kwargs.copy()
            for key in ["thinking", "reasoning_effort"]:
                sanitized_kwargs.pop(key, None)

            processed_messages = self._process_messages(messages)

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=extra_body,
                **sanitized_kwargs,
            )

            msg = response.choices[0].message
            content = msg.content or ""
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
        extra_body: Optional[Dict] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        try:
            # Clean up kwargs to remove custom parameters not supported by the base OpenAI SDK
            sanitized_kwargs = kwargs.copy()
            for key in ["thinking", "reasoning_effort"]:
                sanitized_kwargs.pop(key, None)

            processed_messages = self._process_messages(messages)

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_body=extra_body,
                **sanitized_kwargs,
            )

            for chunk in response:
                if not chunk.choices:
                    continue
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

    def list_models(self) -> List[str]:
        """Fetch models from the provider's API."""
        try:
            # Not all OpenAI-compatible providers allow listing models
            response = self.client.models.list()
            return [m.id for m in response.data]
        except Exception:
            return []
