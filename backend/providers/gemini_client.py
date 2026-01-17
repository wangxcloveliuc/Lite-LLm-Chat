from typing import List, Dict, AsyncIterator, Optional, Tuple
import traceback
import uuid
import json
import base64
import os
import mimetypes
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
        # Check if thinking is explicitly mentioned in model name or in the whitelist
        lowered_model = model.lower()
        if "thinking" in lowered_model:
            return True
        model_name = model[len("models/"):] if model.startswith("models/") else model
        return any(model_name.startswith(prefix) for prefix in self._THINKING_MODELS)

    def _is_imagen_model(self, model: str) -> bool:
        model_name = model[len("models/"):] if model.startswith("models/") else model
        return model_name.lower().startswith("imagen-")

    def _build_imagen_config(self, kwargs: Dict) -> Dict:
        config: Dict[str, object] = {}
        if kwargs.get("imagen_number_of_images") is not None:
            config["number_of_images"] = kwargs.get("imagen_number_of_images")
        if kwargs.get("imagen_image_size"):
            config["image_size"] = kwargs.get("imagen_image_size")
        if kwargs.get("imagen_aspect_ratio"):
            config["aspect_ratio"] = kwargs.get("imagen_aspect_ratio")
        if kwargs.get("imagen_person_generation"):
            config["person_generation"] = kwargs.get("imagen_person_generation")
        return config

    def _normalize_imagen_config(self, config: Dict) -> Optional[object]:
        if not config:
            return None
        config_cls = getattr(self._types, "GenerateImagesConfig", None)
        if config_cls is None:
            config_cls = getattr(self._types, "ImageGenerationConfig", None)
        if config_cls is None:
            return config
        try:
            return config_cls(**config)
        except Exception as e:
            print(f"[GeminiClient] Failed to build Imagen config: {e}. Falling back to raw config.")
            return config

    def _format_image_markdown(self, images) -> str:
        if not images:
            return ""

        def _extract_url(image_obj) -> str:
            if isinstance(image_obj, dict):
                image_url = image_obj.get("image_url") or image_obj.get("imageUrl") or {}
                if isinstance(image_url, dict):
                    return image_url.get("url", "") or image_url.get("uri", "")
                return image_url or image_obj.get("url", "")
            image_url = getattr(image_obj, "image_url", None) or getattr(image_obj, "imageUrl", None)
            if isinstance(image_url, dict):
                return image_url.get("url", "") or image_url.get("uri", "")
            if image_url:
                return image_url
            return getattr(image_obj, "url", "") or ""

        urls = [_extract_url(image) for image in images]
        return "\n\n".join([f"![image]({url})" for url in urls if url])

    def _save_generated_image(self, image_bytes: bytes, mime_type: Optional[str]) -> str:
        if not image_bytes:
            return ""
        ext = ".png"
        if mime_type:
            guessed_ext = mimetypes.guess_extension(mime_type)
            if guessed_ext:
                ext = guessed_ext
        filename = f"gemini_imagen_{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        return f"/uploads/{filename}"

    def _get_safety_settings(self, threshold: str) -> List[Dict[str, str]]:
        if not threshold:
            return None
        categories = [
            "HARM_CATEGORY_HARASSMENT",
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
            "HARM_CATEGORY_CIVIC_INTEGRITY",
        ]
        return [{"category": cat, "threshold": threshold} for cat in categories]

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

            if isinstance(content, list):
                parts = []
                for part in content:
                    if part.get("type") == "text":
                        parts.append({"text": part.get("text") or ""})
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url")
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
                                        parts.append({
                                            "inline_data": {
                                                "mime_type": mime_type,
                                                "data": base64.b64encode(image_file.read()).decode('utf-8')
                                            }
                                        })
                                else:
                                    print(f"[GeminiClient] Image not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading image {url}: {e}")
                    elif part.get("type") == "video_url":
                        url = part.get("video_url", {}).get("url")
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
                                        parts.append({
                                            "inline_data": {
                                                "mime_type": mime_type,
                                                "data": base64.b64encode(video_file.read()).decode('utf-8')
                                            }
                                        })
                                else:
                                    print(f"[GeminiClient] Video not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading video {url}: {e}")
                    elif part.get("type") == "audio_url":
                        url = part.get("audio_url", {}).get("url")
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
                                        parts.append({
                                            "inline_data": {
                                                "mime_type": mime_type,
                                                "data": base64.b64encode(audio_file.read()).decode('utf-8')
                                            }
                                        })
                                else:
                                    print(f"[GeminiClient] Audio not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading audio {url}: {e}")
                        elif url and url.startswith("http"):
                             # Gemini google-genai SDK might not support remote URLs in inline_data easily
                             # For now, we skip or could fetch + base64 if needed.
                             pass
                contents.append(
                    {
                        "role": g_role,
                        "parts": parts,
                    }
                )
            else:
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
        **kwargs,
    ) -> AsyncIterator[str]:
        try:
            if self._is_imagen_model(model):
                content, _reasoning = await self._handle_imagen(model, messages, **kwargs)
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                return
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            
            thinking_budget = kwargs.get("thinking_budget")
            if thinking_budget is None:
                thinking_budget = -1 # Default to unlimited if model supports it
                
            thinking_cfg = (
                self._types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=thinking_budget,
                )
                if enable_thinking
                else None
            )

            # Safety settings
            safety_threshold = kwargs.get("safety_threshold")
            safety_settings = self._get_safety_settings(safety_threshold) if safety_threshold else None

            # Stop sequences
            stop = kwargs.get("stop")
            if isinstance(stop, str):
                stop = [stop]

            config = self._types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=kwargs.get("top_p"),
                top_k=kwargs.get("top_k"),
                presence_penalty=kwargs.get("presence_penalty"),
                frequency_penalty=kwargs.get("frequency_penalty"),
                seed=kwargs.get("seed"),
                stop_sequences=stop,
                system_instruction=system_instruction,
                thinking_config=thinking_cfg,
                safety_settings=safety_settings,
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
        **kwargs,
    ) -> Tuple[str, str]:
        try:
            if self._is_imagen_model(model):
                return await self._handle_imagen(model, messages, **kwargs)
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            
            thinking_budget = kwargs.get("thinking_budget")
            if thinking_budget is None:
                thinking_budget = -1 # Default to unlimited if model supports it
                
            thinking_cfg = (
                self._types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=thinking_budget,
                )
                if enable_thinking
                else None
            )

            # Safety settings
            safety_threshold = kwargs.get("safety_threshold")
            safety_settings = self._get_safety_settings(safety_threshold) if safety_threshold else None

            # Stop sequences
            stop = kwargs.get("stop")
            if isinstance(stop, str):
                stop = [stop]

            config = self._types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=kwargs.get("top_p"),
                top_k=kwargs.get("top_k"),
                presence_penalty=kwargs.get("presence_penalty"),
                frequency_penalty=kwargs.get("frequency_penalty"),
                seed=kwargs.get("seed"),
                stop_sequences=stop,
                system_instruction=system_instruction,
                thinking_config=thinking_cfg,
                safety_settings=safety_settings,
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

    async def _handle_imagen(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> Tuple[str, str]:
        prompt = ""
        for msg in reversed(messages):
            if msg.get("role") != "user":
                continue
            content = msg.get("content")
            if isinstance(content, str):
                prompt = content
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        prompt = part.get("text", "")
                        break
            if prompt:
                break

        config = self._normalize_imagen_config(self._build_imagen_config(kwargs))
        try:
            print(
                f"[GeminiClient] Imagen request model={model}, prompt_len={len(prompt)}, config={config}"
            )
            response = self._client.models.generate_images(
                model=model,
                prompt=prompt,
                config=config,
            )

            images = getattr(response, "images", None)
            if images is None and hasattr(response, "generated_images"):
                images = getattr(response, "generated_images")
            if images is None and isinstance(response, dict):
                images = response.get("images") or response.get("generated_images")

            content = self._format_image_markdown(images)
            if not content and images:
                saved_urls = []
                for image in images:
                    image_obj = getattr(image, "image", None) or image
                    image_bytes = getattr(image_obj, "image_bytes", None)
                    mime_type = getattr(image_obj, "mime_type", None)
                    if image_bytes:
                        saved_url = self._save_generated_image(image_bytes, mime_type)
                        if saved_url:
                            saved_urls.append(saved_url)
                if saved_urls:
                    content = "\n\n".join([f"![image]({url})" for url in saved_urls])
            if not content:
                print(f"[GeminiClient] Imagen response missing images: {response}")
            return content, ""
        except Exception as e:
            print(
                f"[GeminiClient] Imagen generation failed for model={model}: {e}\n{traceback.format_exc()}"
            )
            raise Exception(f"Gemini Imagen error: {str(e)}")

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
