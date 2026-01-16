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

    def _format_image_markdown(self, images) -> str:
        """Convert image outputs to markdown for downstream localization/display."""
        if not images:
            return ""

        def _extract_url(image_obj) -> str:
            if isinstance(image_obj, dict):
                image_url = image_obj.get("image_url") or image_obj.get("imageUrl") or {}
                if isinstance(image_url, dict):
                    return image_url.get("url", "") or image_url.get("uri", "")
                return image_url or ""
            image_url = getattr(image_obj, "image_url", None) or getattr(image_obj, "imageUrl", None)
            if isinstance(image_url, dict):
                return image_url.get("url", "") or image_url.get("uri", "")
            if image_url:
                return image_url
            return getattr(image_obj, "url", "") or ""

        urls = [_extract_url(image) for image in images]
        return "\n\n".join([f"![image]({url})" for url in urls if url])

    def _process_messages(
        self,
        messages: List[Dict],
        image_detail: Optional[str] = None,
        image_pixel_limit: Optional[Dict] = None,
        fps: Optional[float] = None,
        video_detail: Optional[str] = None,
        max_frames: Optional[int] = None,
    ) -> List[Dict]:
        """Process messages to convert local image/video/audio URLs to data URIs."""
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
                                        if image_detail:
                                            new_part["image_url"]["detail"] = image_detail
                                        if image_pixel_limit:
                                            new_part["image_url"]["image_pixel_limit"] = image_pixel_limit
                                        new_parts.append(new_part)
                                        continue
                                else:
                                    print(f"[OpenAIClient] Image not found: {local_path}")
                            except Exception as e:
                                print(f"[OpenAIClient] Error processing image {url}: {e}")
                    
                    # Handle video_url for generic OpenAI-compatible providers
                    elif part.get("type") == "video_url" and "video_url" in part:
                        url = part["video_url"].get("url", "")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "video/mp4"
                                    with open(local_path, "rb") as video_file:
                                        base64_video = base64.b64encode(video_file.read()).decode("utf-8")
                                        new_part = part.copy()
                                        new_part["video_url"] = {"url": f"data:{mime_type};base64,{base64_video}"}
                                        if fps is not None:
                                            new_part["video_url"]["fps"] = fps
                                        if video_detail:
                                            new_part["video_url"]["detail"] = video_detail
                                        if max_frames:
                                            new_part["video_url"]["max_frames"] = max_frames
                                        new_parts.append(new_part)
                                        continue
                                else:
                                    print(f"[OpenAIClient] Video not found: {local_path}")
                            except Exception as e:
                                print(f"[OpenAIClient] Error processing video {url}: {e}")

                    # Handle audio_url for generic OpenAI-compatible providers
                    elif part.get("type") == "audio_url" and "audio_url" in part:
                        url = part["audio_url"].get("url", "")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "audio/mpeg"
                                    with open(local_path, "rb") as audio_file:
                                        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
                                        new_part = part.copy()
                                        new_part["audio_url"] = {"url": f"data:{mime_type};base64,{base64_audio}"}
                                        new_parts.append(new_part)
                                        continue
                                else:
                                    print(f"[OpenAIClient] Audio not found: {local_path}")
                            except Exception as e:
                                print(f"[OpenAIClient] Error processing audio {url}: {e}")

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
            # Clean up kwargs to remove custom parameters not supported by the base OpenAI SDK
            sanitized_kwargs = kwargs.copy()
            image_detail = sanitized_kwargs.pop("image_detail", None)
            image_pixel_limit = sanitized_kwargs.pop("image_pixel_limit", None)
            fps = sanitized_kwargs.pop("fps", None)
            video_detail = sanitized_kwargs.pop("video_detail", None)
            max_frames = sanitized_kwargs.pop("max_frames", None)
            
            # Remove all extended settings that are not part of standard OpenAI chat/completions/create
            extended_keys = [
                "thinking", "reasoning_effort", "disable_reasoning", "reasoning_format", 
                "include_reasoning", "max_completion_tokens", "enable_thinking", 
                "thinking_budget", "min_p", "top_k",
                # OpenRouter-specific
                "transforms", "models", "route", "repetition_penalty", "top_a", "logprobs",
                "top_logprobs", "response_format", "structured_outputs", "parallel_tool_calls",
                "reasoning", "modalities", "image_config"
            ]

            # For OpenRouter, we might want to keep some of these in extra_body
            or_keys = [
                "transforms", "models", "route", "repetition_penalty", "top_a", "logprobs",
                "top_logprobs", "response_format", "structured_outputs", "parallel_tool_calls",
                "reasoning", "modalities", "image_config"
            ]
            _extra_body = extra_body.copy() if extra_body else {}
            for key in or_keys:
                if key in sanitized_kwargs:
                    _extra_body[key] = sanitized_kwargs.pop(key)
            
            curr_extra_body = _extra_body if _extra_body else extra_body

            for key in extended_keys:
                sanitized_kwargs.pop(key, None)

            # Fix for reasoning models that don't support certain parameters
            # e.g. grok-4-fast-reasoning, o1-preview, etc.
            is_reasoning_model = any(slug in model.lower() for slug in ["reasoning", "o1-", "o3-"])
            
            if is_reasoning_model:
                sanitized_kwargs.pop("presence_penalty", None)
                sanitized_kwargs.pop("frequency_penalty", None)
                # Some reasoning models don't support temperature=1, they require exactly 1 or omit
                # But let's stay focused on the presence_penalty first
            else:
                if sanitized_kwargs.get("presence_penalty") == 0:
                    sanitized_kwargs.pop("presence_penalty", None)
                if sanitized_kwargs.get("frequency_penalty") == 0:
                    sanitized_kwargs.pop("frequency_penalty", None)

            processed_messages = self._process_messages(
                messages, 
                image_detail=image_detail, 
                image_pixel_limit=image_pixel_limit,
                fps=fps,
                video_detail=video_detail,
                max_frames=max_frames
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                extra_body=curr_extra_body,
                **sanitized_kwargs,
            )

            msg = response.choices[0].message
            content = msg.content or ""
            image_markdown = self._format_image_markdown(getattr(msg, "images", None))
            if image_markdown:
                content = f"{content}\n\n{image_markdown}" if content else image_markdown
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
            image_detail = sanitized_kwargs.pop("image_detail", None)
            image_pixel_limit = sanitized_kwargs.pop("image_pixel_limit", None)
            fps = sanitized_kwargs.pop("fps", None)
            video_detail = sanitized_kwargs.pop("video_detail", None)
            max_frames = sanitized_kwargs.pop("max_frames", None)
            
            # Remove all extended settings that are not part of standard OpenAI chat/completions/create
            extended_keys = [
                "thinking", "reasoning_effort", "disable_reasoning", "reasoning_format", 
                "include_reasoning", "max_completion_tokens", "enable_thinking", 
                "thinking_budget", "min_p", "top_k",
                # OpenRouter-specific
                "transforms", "models", "route", "repetition_penalty", "top_a", "logprobs",
                "top_logprobs", "response_format", "structured_outputs", "parallel_tool_calls",
                "reasoning", "modalities", "image_config"
            ]

            # For OpenRouter, we might want to keep some of these in extra_body
            or_keys = [
                "transforms", "models", "route", "repetition_penalty", "top_a", "logprobs",
                "top_logprobs", "response_format", "structured_outputs", "parallel_tool_calls",
                "reasoning", "modalities", "image_config"
            ]
            _extra_body = extra_body.copy() if extra_body else {}
            for key in or_keys:
                if key in sanitized_kwargs:
                    _extra_body[key] = sanitized_kwargs.pop(key)
            
            curr_extra_body = _extra_body if _extra_body else extra_body

            for key in extended_keys:
                sanitized_kwargs.pop(key, None)

            # Fix for reasoning models that don't support certain parameters
            is_reasoning_model = any(slug in model.lower() for slug in ["reasoning", "o1-", "o3-"])
            
            if is_reasoning_model:
                sanitized_kwargs.pop("presence_penalty", None)
                sanitized_kwargs.pop("frequency_penalty", None)
            else:
                if sanitized_kwargs.get("presence_penalty") == 0:
                    sanitized_kwargs.pop("presence_penalty", None)
                if sanitized_kwargs.get("frequency_penalty") == 0:
                    sanitized_kwargs.pop("frequency_penalty", None)

            processed_messages = self._process_messages(
                messages, 
                image_detail=image_detail, 
                image_pixel_limit=image_pixel_limit,
                fps=fps,
                video_detail=video_detail,
                max_frames=max_frames
            )

            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                extra_body=curr_extra_body,
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

                image_markdown = self._format_image_markdown(getattr(delta, "images", None))
                if image_markdown:
                    yield f"data: {json.dumps({'content': image_markdown})}\n\n"

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
