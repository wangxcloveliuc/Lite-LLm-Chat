from typing import AsyncIterator, Dict, List, Optional, Tuple

from .openai_base import OpenAICompatibleClient

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class NvidiaClient(OpenAICompatibleClient):
    """Client for interacting with Nvidia NIM API"""

    def _prepare_extra_body(
        self,
        extra_body: Optional[Dict],
        kwargs: Dict,
    ) -> Tuple[Optional[Dict], Dict]:
        merged_extra_body: Dict = {}
        if extra_body:
            merged_extra_body.update(extra_body)

        kwargs_extra_body = kwargs.pop("extra_body", None)
        if kwargs_extra_body:
            merged_extra_body.update(kwargs_extra_body)

        thinking = kwargs.pop("thinking", None)
        reasoning_effort = kwargs.pop("reasoning_effort", None)

        if thinking is not None:
            chat_template_kwargs = merged_extra_body.setdefault("chat_template_kwargs", {})
            chat_template_kwargs["thinking"] = thinking

        if reasoning_effort is not None:
            merged_extra_body["reasoning_effort"] = reasoning_effort

        return (merged_extra_body or None), kwargs

    def __init__(self):
        super().__init__(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        extra_body: Optional[Dict] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        extra_body, kwargs = self._prepare_extra_body(extra_body, kwargs)
        return await super().chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=extra_body,
            **kwargs,
        )

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        extra_body: Optional[Dict] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        extra_body, kwargs = self._prepare_extra_body(extra_body, kwargs)
        async for chunk in super().stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=extra_body,
            **kwargs,
        ):
            yield chunk


# Singleton instance
nvidia_client = NvidiaClient()
