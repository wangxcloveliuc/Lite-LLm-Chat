import json
import os
import uuid
import re
from typing import List, Optional, Tuple

import httpx


def _ensure_list(data):
    if data is None:
        return None
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            return [data] if data else []
    return data


async def _save_remote_image(url: str) -> str:
    """Download remote image and save to local uploads directory."""
    if not url.startswith("http"):
        return url

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            if response.status_code == 200:
                # Determine extension
                content_type = response.headers.get("content-type", "")
                ext = ".png"
                if "jpeg" in content_type:
                    ext = ".jpg"
                elif "webp" in content_type:
                    ext = ".webp"

                filename = f"{uuid.uuid4()}{ext}"
                upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
                os.makedirs(upload_dir, exist_ok=True)

                filepath = os.path.join(upload_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)

                return f"/uploads/{filename}"
    except Exception as e:
        print(f"Error saving remote image {url}: {e}")

    return url


def _format_api_content(
    content: str,
    images: Optional[List[str]],
    videos: Optional[List[str]] = None,
    audios: Optional[List[str]] = None,
):
    images = _ensure_list(images)
    videos = _ensure_list(videos)
    audios = _ensure_list(audios)
    if not images and not videos and not audios:
        return content

    parts = [{"type": "text", "text": content}]
    if images:
        for img_url in images:
            parts.append({"type": "image_url", "image_url": {"url": img_url}})
    if videos:
        for video_url in videos:
            parts.append({"type": "video_url", "video_url": {"url": video_url}})
    if audios:
        for audio_url in audios:
            parts.append({"type": "audio_url", "audio_url": {"url": audio_url}})
    return parts


def _build_provider_kwargs(chat_request):
    provider_kwargs = {
        "temperature": chat_request.temperature,
        "max_tokens": chat_request.max_tokens,
        "frequency_penalty": chat_request.frequency_penalty,
        "presence_penalty": chat_request.presence_penalty,
        "top_p": chat_request.top_p,
        "stop": chat_request.stop,
    }

    if chat_request.thinking is not None:
        provider_kwargs["thinking"] = chat_request.thinking
    if chat_request.reasoning_effort is not None:
        provider_kwargs["reasoning_effort"] = chat_request.reasoning_effort
    if chat_request.disable_reasoning is not None:
        provider_kwargs["disable_reasoning"] = chat_request.disable_reasoning
    if chat_request.reasoning_format is not None:
        provider_kwargs["reasoning_format"] = chat_request.reasoning_format
    if chat_request.include_reasoning is not None:
        provider_kwargs["include_reasoning"] = chat_request.include_reasoning
    if chat_request.max_completion_tokens is not None:
        provider_kwargs["max_completion_tokens"] = chat_request.max_completion_tokens
    if chat_request.enable_thinking is not None:
        provider_kwargs["enable_thinking"] = chat_request.enable_thinking
    if chat_request.thinking_budget is not None:
        provider_kwargs["thinking_budget"] = chat_request.thinking_budget
    if chat_request.min_p is not None:
        provider_kwargs["min_p"] = chat_request.min_p
    if chat_request.top_k is not None:
        provider_kwargs["top_k"] = chat_request.top_k
    if chat_request.safe_prompt is not None:
        provider_kwargs["safe_prompt"] = chat_request.safe_prompt
    if chat_request.random_seed is not None:
        provider_kwargs["random_seed"] = chat_request.random_seed

    # Doubao Seedream specific
    if chat_request.sequential_image_generation is not None:
        provider_kwargs["sequential_image_generation"] = chat_request.sequential_image_generation
    if chat_request.max_images is not None:
        provider_kwargs["max_images"] = chat_request.max_images
    if chat_request.watermark is not None:
        provider_kwargs["watermark"] = chat_request.watermark
    if chat_request.prompt_optimize_mode is not None:
        provider_kwargs["prompt_optimize_mode"] = chat_request.prompt_optimize_mode
    if chat_request.size is not None:
        provider_kwargs["size"] = chat_request.size
    if chat_request.seed is not None:
        provider_kwargs["seed"] = chat_request.seed
    if chat_request.image_detail is not None:
        provider_kwargs["image_detail"] = chat_request.image_detail
    if chat_request.image_pixel_limit is not None:
        # In some Pydantic versions/configs, nested models might already be dicts here if bypass validation occurred
        # or if they are plain dicts from the request.
        limit = chat_request.image_pixel_limit
        if isinstance(limit, dict):
            provider_kwargs["image_pixel_limit"] = {k: v for k, v in limit.items() if v is not None}
        elif hasattr(limit, "model_dump"):
            provider_kwargs["image_pixel_limit"] = limit.model_dump(exclude_none=True)
        elif hasattr(limit, "dict"):
            provider_kwargs["image_pixel_limit"] = limit.dict(exclude_none=True)
        else:
            provider_kwargs["image_pixel_limit"] = limit
    if chat_request.fps is not None:
        provider_kwargs["fps"] = chat_request.fps
    if chat_request.video_detail is not None:
        provider_kwargs["video_detail"] = chat_request.video_detail
    if chat_request.max_frames is not None:
        provider_kwargs["max_frames"] = chat_request.max_frames

    # Doubao Seedance specific
    if chat_request.resolution is not None:
        provider_kwargs["resolution"] = chat_request.resolution
    if chat_request.ratio is not None:
        provider_kwargs["ratio"] = chat_request.ratio
    if chat_request.duration is not None:
        provider_kwargs["duration"] = chat_request.duration
    if chat_request.generate_audio is not None:
        provider_kwargs["generate_audio"] = chat_request.generate_audio
    if chat_request.draft is not None:
        provider_kwargs["draft"] = chat_request.draft
    if chat_request.camera_fixed is not None:
        provider_kwargs["camera_fixed"] = chat_request.camera_fixed

    return provider_kwargs


async def _localize_markdown_images(content: str) -> Tuple[str, List[str]]:
    img_pattern = r"!\[image\]\((https?://[^\)]+)\)"
    matches = re.finditer(img_pattern, content)

    found_urls = []
    for match in matches:
        original_url = match.group(1)
        local_path = await _save_remote_image(original_url)
        if local_path != original_url:
            content = content.replace(original_url, local_path)
            found_urls.append(local_path)

    return content, found_urls


async def _localize_streaming_content(content_val: str) -> Tuple[str, bool]:
    if "! [image]" not in content_val and "![" not in content_val:
        return content_val, False

    img_pattern = r"!\[image\]\((https?://[^\)]+)\)"
    matches = re.finditer(img_pattern, content_val)
    modified = False
    for match in matches:
        original_url = match.group(1)
        local_path = await _save_remote_image(original_url)
        if local_path != original_url:
            content_val = content_val.replace(original_url, local_path)
            modified = True

    return content_val, modified
