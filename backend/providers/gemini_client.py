from typing import List, Dict, AsyncIterator, Optional, Tuple
import json
import traceback

from google import genai
from google.genai import types

from .base import BaseClient
from .gemini_config import GeminiConfigMixin
from .gemini_media import GeminiMediaMixin
from .gemini_messages import GeminiMessagesMixin
from .gemini_response import GeminiResponseMixin

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GeminiClient(
    GeminiConfigMixin,
    GeminiMediaMixin,
    GeminiMessagesMixin,
    GeminiResponseMixin,
    BaseClient,
):

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
        self._last_thought_signatures: List[str] = []
        self._last_search_results: List[Dict[str, str]] = []

    async def _handle_gemini_image_generation(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> Tuple[str, str]:
        contents, system_instruction = self._messages_to_contents_and_system(messages)
        response_modalities = self._normalize_response_modalities(kwargs.get("modalities"))
        image_config = self._normalize_image_config(kwargs.get("image_config"))
        media_resolution = self._normalize_media_resolution(kwargs.get("media_resolution"))
        thinking_level = (
            kwargs.get("thinking_level") if self._supports_thinking_level(model) else None
        )
        tools = self._merge_tools(
            self._build_tools(kwargs.get("google_search")),
            self._build_url_context_tool(kwargs.get("url_context")),
        )
        thinking_cfg = (
            self._types.ThinkingConfig(thinking_level=thinking_level, include_thoughts=True)
            if thinking_level
            else None
        )

        config = self._types.GenerateContentConfig(
            temperature=kwargs.get("temperature", 1),
            max_output_tokens=kwargs.get("max_tokens"),
            top_p=kwargs.get("top_p"),
            top_k=kwargs.get("top_k"),
            presence_penalty=kwargs.get("presence_penalty"),
            frequency_penalty=kwargs.get("frequency_penalty"),
            seed=kwargs.get("seed"),
            system_instruction=system_instruction,
            response_modalities=response_modalities,
            image_config=image_config,
            thinking_config=thinking_cfg,
            media_resolution=media_resolution,
            tools=tools,
        )

        response = await self._client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        self._last_thought_signatures = self._extract_thought_signatures(response)
        self._last_search_results = (
            self._extract_search_results(response)
            or self._extract_url_context_results(response)
        )

        text = self._extract_regular_text_from_response(response)
        images = self._extract_inline_images(response)
        saved_urls = [self._save_generated_image(img, mime) for img, mime in images]
        markdown = "\n\n".join([f"![image]({url})" for url in saved_urls if url])
        if text and markdown:
            content = f"{text}\n\n{markdown}"
        else:
            content = text or markdown
        return content, ""

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        try:
            self._last_thought_signatures = []
            self._last_search_results = []
            if self._is_imagen_model(model):
                content, _reasoning = await self._handle_imagen(model, messages, **kwargs)
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                return
            if self._is_gemini_image_model(model):
                content, _reasoning = await self._handle_gemini_image_generation(model, messages, **kwargs)
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                return
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            thinking_level = (
                kwargs.get("thinking_level") if self._supports_thinking_level(model) else None
            )
            media_resolution = self._normalize_media_resolution(kwargs.get("media_resolution"))
            tools = self._merge_tools(
                self._build_tools(kwargs.get("google_search")),
                self._build_url_context_tool(kwargs.get("url_context")),
            )

            thinking_budget = kwargs.get("thinking_budget")
            if thinking_budget is None:
                thinking_budget = -1  # Default to unlimited if model supports it

            if thinking_level:
                thinking_cfg = self._types.ThinkingConfig(
                    thinking_level=thinking_level,
                    include_thoughts=True,
                )
            else:
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
                media_resolution=media_resolution,
                tools=tools,
            )

            # The SDK provides async streaming under client.aio
            async for chunk in await self._client.aio.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            ):
                search_results = self._extract_search_results(chunk)
                if not search_results:
                    search_results = self._extract_url_context_results(chunk)
                if search_results:
                    self._last_search_results = search_results
                    yield f"data: {json.dumps({'search_results': search_results})}\n\n"
                signatures = self._extract_thought_signatures(chunk)
                if signatures:
                    self._last_thought_signatures = signatures
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
            self._last_thought_signatures = []
            self._last_search_results = []
            if self._is_imagen_model(model):
                return await self._handle_imagen(model, messages, **kwargs)
            if self._is_gemini_image_model(model):
                return await self._handle_gemini_image_generation(model, messages, **kwargs)
            contents, system_instruction = self._messages_to_contents_and_system(messages)

            # Only enable thinking for specific models
            enable_thinking = self._should_enable_thinking(model)
            thinking_level = (
                kwargs.get("thinking_level") if self._supports_thinking_level(model) else None
            )
            media_resolution = self._normalize_media_resolution(kwargs.get("media_resolution"))
            tools = self._build_tools(kwargs.get("google_search"))

            thinking_budget = kwargs.get("thinking_budget")
            if thinking_budget is None:
                thinking_budget = -1  # Default to unlimited if model supports it

            if thinking_level:
                thinking_cfg = self._types.ThinkingConfig(
                    thinking_level=thinking_level,
                    include_thoughts=True,
                )
            else:
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
                media_resolution=media_resolution,
                tools=tools,
            )

            response = await self._client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            self._last_thought_signatures = self._extract_thought_signatures(response)
            self._last_search_results = (
                self._extract_search_results(response)
                or self._extract_url_context_results(response)
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
