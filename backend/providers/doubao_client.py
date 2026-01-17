import asyncio
import base64
import json
import mimetypes
import os
import uuid
from typing import AsyncIterator, Dict, List, Optional, Tuple

import httpx
from pydantic import BaseModel
from volcenginesdkarkruntime import Ark

from .base import BaseClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class _SeedreamSequentialImageGenerationOptions(BaseModel):
    max_images: Optional[int] = None


class _SeedreamOptimizePromptOptions(BaseModel):
    mode: Optional[str] = None


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
        fps: Optional[float] = None,
    ) -> List[Dict]:
        """Convert local image/video URLs to data URIs for Ark multi-modal support."""
        new_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if isinstance(content, list):
                new_parts = []
                for part in content:
                    # Handle image_url
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
                            except Exception as e:
                                print(f"[DoubaoArk] Error processing image {url}: {e}")
                    
                    # Handle video_url
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
                                        new_parts.append(new_part)
                                        continue
                            except Exception as e:
                                print(f"[DoubaoArk] Error processing video {url}: {e}")

                    new_parts.append(part)
                new_messages.append({"role": role, "content": new_parts})
            else:
                new_messages.append(msg)
        return new_messages

    def _is_seedream(self, model: str) -> bool:
        """Check if the model is a Seedream image generation model."""
        return "seedream" in model.lower()

    def _is_seedance(self, model: str) -> bool:
        """Check if the model is a Seedance video generation model."""
        return "seedance" in model.lower()

    def _supports_reasoning_effort(self, model: str) -> bool:
        """Check if the model supports reasoning_effort parameter."""
        return "seed-code-preview" not in model.lower()

    def _prepare_chat_request(
        self,
        model: str,
        messages: List[Dict],
        kwargs: Dict,
    ) -> Tuple[List[Dict], Dict, Dict]:
        extra_body = kwargs.pop("extra_body", {}) or {}
        thinking = kwargs.pop("thinking", None)
        reasoning_effort = kwargs.pop("reasoning_effort", None)
        max_completion_tokens = kwargs.pop("max_completion_tokens", None)
        image_detail = kwargs.pop("image_detail", None)
        image_pixel_limit = kwargs.pop("image_pixel_limit", None)
        fps = kwargs.pop("fps", None)
        kwargs.pop("video_detail", None)
        kwargs.pop("max_frames", None)

        for key in [
            "disable_reasoning",
            "reasoning_format",
            "include_reasoning",
            "enable_thinking",
            "thinking_budget",
            "min_p",
            "top_k",
        ]:
            kwargs.pop(key, None)

        if thinking is True:
            extra_body["thinking"] = {"type": "enabled"}
        elif thinking is False:
            extra_body["thinking"] = {"type": "disabled"}

        if reasoning_effort and self._supports_reasoning_effort(model):
            extra_body["reasoning_effort"] = reasoning_effort

        if max_completion_tokens is not None:
            kwargs["max_completion_tokens"] = max_completion_tokens

        processed_messages = self._process_messages(
            messages,
            image_detail=image_detail,
            image_pixel_limit=image_pixel_limit,
            fps=fps,
        )
        return processed_messages, extra_body, kwargs

    async def _download_and_save_video(self, video_url: str) -> str:
        """Download video from URL and save to local uploads directory."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            uploads_dir = os.path.join(backend_dir, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)

            filename = f"doubao_video_{uuid.uuid4().hex}.mp4"
            local_path = os.path.join(uploads_dir, filename)

            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, timeout=60.0)
                response.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(response.content)
            
            # Return relative path for frontend
            return f"/uploads/{filename}"
        except Exception as e:
            print(f"[DoubaoArk] Error downloading video: {e}")
            return video_url

    async def _handle_seedance(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> Tuple[str, str]:
        """Handle asynchronous video generation for Seedance models using SDK."""
        processed_messages = self._process_messages(messages)
        
        # Extract prompt and reference images
        prompt = ""
        image_parts = []
        for msg in reversed(processed_messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    prompt = content
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            prompt = part.get("text", "")
                        elif part.get("type") == "image_url":
                            image_parts.append(part)
                if prompt:
                    break

        # Build content list with logic: 1 -> first_frame, 2 -> first/last, >2 -> reference
        api_content = [{"type": "text", "text": prompt}]
        
        for i, img_part in enumerate(image_parts):
            new_img = img_part.copy()
            if len(image_parts) == 1:
                new_img["role"] = "first_frame"
            elif len(image_parts) == 2:
                new_img["role"] = "first_frame" if i == 0 else "last_frame"
            else:
                new_img["role"] = "reference_image"
            api_content.append(new_img)

        # Prepare SDK parameters
        # Common params
        task_params = {
            "model": model,
            "content": api_content,
            "ratio": kwargs.get("ratio", "16:9"),
            "resolution": kwargs.get("resolution", "720p"),
            "duration": int(kwargs.get("duration", 5)) if kwargs.get("duration") else 5,
            "watermark": kwargs.get("watermark", False),
        }
        
        # Seedance 1.5 specifics (Audio & Draft)
        if "1-5" in model:
            if "generate_audio" in kwargs:
                task_params["generate_audio"] = kwargs.get("generate_audio")
            if "draft" in kwargs:
                task_params["draft"] = kwargs.get("draft")
        
        seed = kwargs.get("seed", -1)
        if seed is not None and seed != -1:
            task_params["seed"] = seed
            
        if kwargs.get("camera_fixed"):
            task_params["camera_fixed"] = True

        try:
            # 1. Create Task using SDK
            print(f"[DoubaoArk] Creating Seedance task with model: {model}")
            task_resp = self.client.content_generation.tasks.create(**task_params)
            task_id = getattr(task_resp, "id", None)
            if not task_id:
                raise Exception(f"No task ID returned from SDK: {task_resp}")

            print(f"[DoubaoArk] Created Seedance task {task_id}")

            # 2. Polling using SDK
            max_retries = 120 # 10 minutes max with 5s sleep
            for _ in range(max_retries):
                await asyncio.sleep(5)
                
                # Get task status using SDK
                status_resp = self.client.content_generation.tasks.get(task_id=task_id)
                status = getattr(status_resp, "status", "unknown")
                
                if status == "succeeded":
                    # Extract video URL from nested content object
                    gen_content = getattr(status_resp, "content", None)
                    video_url = getattr(gen_content, "video_url", None) if gen_content else None
                    
                    if video_url:
                        print(f"[DoubaoArk] Task {task_id} succeeded, downloading video...")
                        local_video_path = await self._download_and_save_video(video_url)
                        return f"Video generated: ![video]({local_video_path})", ""
                    else:
                        return "Video generation succeeded but no URL found in response.", ""
                
                elif status == "failed":
                    error_info = getattr(status_resp, "error", None)
                    err_msg = getattr(error_info, "message", "Unknown error") if error_info else "Unknown API error"
                    raise Exception(f"Video generation failed: {err_msg}")
                
                elif status == "expired":
                    raise Exception("Video generation task expired on server.")
                
                elif status in ["queued", "running"]:
                    continue
                else:
                    print(f"[DoubaoArk] Task {task_id} in unexpected status: {status}")
            
            raise Exception("Video generation timed out after 10 minutes.")

        except Exception as e:
            print(f"[DoubaoArk] Seedance SDK error: {e}")
            raise Exception(f"Seedance SDK error: {str(e)}")

    async def _handle_seedream(
        self,
        model: str,
        messages: List[Dict],
        **kwargs
    ) -> Tuple[str, str]:
        """Handle non-streaming image generation for Seedream models."""
        processed_messages = self._process_messages(messages)
        
        # Extract prompt and reference images from messages
        prompt = ""
        images = []
        for msg in reversed(processed_messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    prompt = content
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            prompt = part.get("text", "")
                        elif part.get("type") == "image_url":
                            url = part.get("image_url", {}).get("url")
                            if url:
                                images.append(url)
                if prompt:
                    break

        # Process parameters
        size = kwargs.pop("size", "2048x2048")
        seed = kwargs.pop("seed", None)
        sequential_image_generation = kwargs.pop("sequential_image_generation", "disabled")
        max_images = kwargs.pop("max_images", 15)
        watermark = kwargs.pop("watermark", True)
        prompt_optimize_mode = kwargs.pop("prompt_optimize_mode", "standard")
        
        # Prepare request body
        request_params = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "watermark": watermark,
        }
        if images:
            request_params["image"] = images
        if seed is not None and seed != -1:
            request_params["seed"] = seed
        if sequential_image_generation == "auto":
            request_params["sequential_image_generation"] = "auto"
            request_params["sequential_image_generation_options"] = _SeedreamSequentialImageGenerationOptions(
                max_images=max_images
            )
        if prompt_optimize_mode:
            request_params["optimize_prompt_options"] = _SeedreamOptimizePromptOptions(mode=prompt_optimize_mode)

        try:
            # Use generate or completions depending on SDK
            # Based on our check, client.images.generate exists
            print(f"[DoubaoArk] Seedream Request: {request_params}")
            response = self.client.images.generate(**request_params)
            print(f"[DoubaoArk] Seedream Response: {response}")
            
            content_parts = []
            if hasattr(response, "data") and response.data:
                for img in response.data:
                    url = ""
                    if isinstance(img, dict):
                        url = img.get("url", "")
                    else:
                        # Try attribute access for Pydantic models/objects
                        url = getattr(img, "url", "")
                    
                    if url:
                        content_parts.append(f"![image]({url})")
            
            if not content_parts:
                print(f"[DoubaoArk] No images found in response data: {getattr(response, 'data', 'N/A')}")
            
            return "\n\n".join(content_parts), ""
        except Exception as e:
            print(f"[DoubaoArk] Seedream API error: {str(e)}")
            raise Exception(f"Seedream API error: {str(e)}")

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        if self._is_seedream(model):
            return await self._handle_seedream(model, messages, **kwargs)
        if self._is_seedance(model):
            return await self._handle_seedance(model, messages, **kwargs)

        try:
            processed_messages, extra_body, kwargs = self._prepare_chat_request(model, messages, kwargs)

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
        if self._is_seedream(model):
            try:
                content, _reasoning = await self._handle_seedream(model, messages, **kwargs)
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
            return

        if self._is_seedance(model):
            try:
                content, _reasoning = await self._handle_seedance(model, messages, **kwargs)
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
            return

        try:
            processed_messages, extra_body, kwargs = self._prepare_chat_request(model, messages, kwargs)

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

