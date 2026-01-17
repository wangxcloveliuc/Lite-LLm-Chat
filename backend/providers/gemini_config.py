from typing import Dict, List, Optional


class GeminiConfigMixin:
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

    def _should_enable_thinking(self, model: str) -> bool:
        # Check if thinking is explicitly mentioned in model name or in the whitelist
        lowered_model = model.lower()
        if "thinking" in lowered_model:
            return True
        model_name = model[len("models/"):] if model.startswith("models/") else model
        return any(model_name.startswith(prefix) for prefix in self._THINKING_MODELS)

    def _supports_thinking_level(self, model: str) -> bool:
        model_name = model[len("models/"):] if model.startswith("models/") else model
        return model_name.lower().startswith("gemini-3")

    def _is_imagen_model(self, model: str) -> bool:
        model_name = model[len("models/"):] if model.startswith("models/") else model
        return model_name.lower().startswith("imagen-")

    def _is_gemini_image_model(self, model: str) -> bool:
        model_name = model[len("models/"):] if model.startswith("models/") else model
        lowered = model_name.lower()
        return "image" in lowered and not lowered.startswith("imagen-")

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
            print(
                f"[GeminiClient] Failed to build Imagen config: {e}. Falling back to raw config."
            )
            return config

    def _normalize_response_modalities(self, modalities) -> Optional[List[str]]:
        if not modalities:
            return None
        normalized: List[str] = []
        for m in modalities:
            if not m:
                continue
            val = str(m).strip().upper()
            if val in {"IMAGE", "TEXT"}:
                normalized.append(val)
        return normalized or None

    def _normalize_image_config(self, config: Optional[Dict]) -> Optional[object]:
        if not config:
            return None
        config_cls = getattr(self._types, "ImageConfig", None)
        if config_cls is None:
            return config
        try:
            return config_cls(**config)
        except Exception as e:
            print(f"[GeminiClient] Failed to build image config: {e}. Falling back to raw config.")
            return config

    def _normalize_media_resolution(self, resolution: Optional[str]):
        if not resolution:
            return None
        media_cls = getattr(self._types, "MediaResolution", None)
        if media_cls is None:
            return resolution
        attr = resolution.upper()
        if hasattr(media_cls, attr):
            return getattr(media_cls, attr)
        return resolution

    def _build_tools(self, google_search: Optional[bool]):
        if not google_search:
            return None
        return [self._types.Tool(google_search=self._types.GoogleSearch())]

    def _build_url_context_tool(self, url_context: Optional[bool]):
        if not url_context:
            return None
        if hasattr(self._types, "UrlContext"):
            return self._types.Tool(url_context=self._types.UrlContext())
        return {"url_context": {}}

    def _merge_tools(self, *tools) -> Optional[List[object]]:
        merged: List[object] = []
        for tool in tools:
            if not tool:
                continue
            if isinstance(tool, list):
                merged.extend(tool)
            else:
                merged.append(tool)
        return merged or None

    def _get_safety_settings(self, threshold: str) -> Optional[List[Dict[str, str]]]:
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
