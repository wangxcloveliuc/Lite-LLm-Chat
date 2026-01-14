from typing import List, Optional
from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class GroqClient(OpenAICompatibleClient):
    """Client for interacting with Groq OpenAI-compatible API"""

    def __init__(self):
        super().__init__(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )

    def _prepare_groq_args(self, model: str, **kwargs):
        """Prepare Groq-specific arguments based on documentation."""
        sanitized_kwargs = kwargs.copy()
        
        # Get existing extra_body
        extra_body = sanitized_kwargs.pop("extra_body", {}) or {}
        
        # Check model types
        is_gpt_oss = "gpt-oss" in model.lower()
        is_qwen3 = "qwen3" in model.lower()
        is_reasoning_model = is_gpt_oss or is_qwen3

        # 1. Clean up top-level args that the OpenAI SDK doesn't support
        # Any custom Groq parameter should be in extra_body
        rf = sanitized_kwargs.pop("reasoning_format", None)
        ir = sanitized_kwargs.pop("include_reasoning", None)
        re = sanitized_kwargs.pop("reasoning_effort", None)
        mct = sanitized_kwargs.pop("max_completion_tokens", None)
        mt = sanitized_kwargs.pop("max_tokens", None)

        # 2. Re-assign tokens (Groq prefers max_completion_tokens for all, butmt is safer top-level)
        final_tokens = mct or mt
        if is_reasoning_model:
            # For reasoning models, move to extra_body to ensure compatibility
            if final_tokens:
                extra_body["max_completion_tokens"] = final_tokens
            # Ensure max_tokens is not passed twice or as a conflicting top-level
            sanitized_kwargs["max_tokens"] = None
        else:
            # For standard models, use max_tokens as top-level if provided
            if final_tokens:
                sanitized_kwargs["max_tokens"] = final_tokens

        # 3. Re-assign reasoning fields ONLY if supported by model
        if is_gpt_oss:
            if re in ["low", "medium", "high"]:
                extra_body["reasoning_effort"] = re
            if ir is not None:
                extra_body["include_reasoning"] = ir
        elif is_qwen3:
            if re in ["none", "default"]:
                extra_body["reasoning_effort"] = re
            if rf in ["hidden", "raw", "parsed"]:
                extra_body["reasoning_format"] = rf
            elif ir is not None:
                # Mutual exclusivity usually means rf is better for Qwen
                extra_body["include_reasoning"] = ir
        
        if extra_body:
            sanitized_kwargs["extra_body"] = extra_body
            
        return sanitized_kwargs

    async def chat(self, model: str, *args, **kwargs):
        groq_kwargs = self._prepare_groq_args(model, **kwargs)
        return await super().chat(model, *args, **groq_kwargs)

    async def stream_chat(self, model: str, *args, **kwargs):
        groq_kwargs = self._prepare_groq_args(model, **kwargs)
        async for chunk in super().stream_chat(model, *args, **groq_kwargs):
            yield chunk


# Singleton instance
groq_client = GroqClient()

