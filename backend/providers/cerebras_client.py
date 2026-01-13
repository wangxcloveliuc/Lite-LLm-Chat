from .openai_base import OpenAICompatibleClient
import json
from typing import List, Dict, AsyncIterator, Optional, Tuple

try:
    from ..config import settings
except (ImportError, ValueError):
    from config import settings


class CerebrasClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__(
            api_key=settings.cerebras_api_key,
            base_url=settings.cerebras_base_url,
        )

    def _prepare_cerebras_args(self, model: str, **kwargs):
        """Prepare Cerebras-specific arguments."""
        sanitized_kwargs = kwargs.copy()
        
        # Remove unsupported parameters
        sanitized_kwargs.pop("frequency_penalty", None)
        sanitized_kwargs.pop("presence_penalty", None)
        sanitized_kwargs.pop("logit_bias", None)
        sanitized_kwargs.pop("service_tier", None)
        
        extra_body = sanitized_kwargs.pop("extra_body", {}) or {}
        
        # reasoning_effort for gpt-oss models via extra_body
        reasoning_effort = sanitized_kwargs.pop("reasoning_effort", None)
        if "gpt-oss" in model.lower() and reasoning_effort:
            extra_body["reasoning_effort"] = reasoning_effort
            
        # disable_reasoning for zai models via extra_body
        disable_reasoning = sanitized_kwargs.pop("disable_reasoning", None)
        if "zai" in model.lower() and disable_reasoning is not None:
            extra_body["disable_reasoning"] = disable_reasoning
            
        if extra_body:
            sanitized_kwargs["extra_body"] = extra_body
            
        return sanitized_kwargs

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        cerebras_kwargs = self._prepare_cerebras_args(model, **kwargs)
        
        try:
            image_detail = cerebras_kwargs.pop("image_detail", None)
            image_pixel_limit = cerebras_kwargs.pop("image_pixel_limit", None)
            fps = cerebras_kwargs.pop("fps", None)
            video_detail = cerebras_kwargs.pop("video_detail", None)
            max_frames = cerebras_kwargs.pop("max_frames", None)

            processed_messages = self._process_messages(
                messages, 
                image_detail=image_detail, 
                image_pixel_limit=image_pixel_limit,
                fps=fps,
                video_detail=video_detail,
                max_frames=max_frames
            )

            # We need to manually handle temperature=1 as default if not passed, 
            # or just pass it if it's there.
            response = self.client.chat.completions.create(
                model=model,
                messages=processed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **cerebras_kwargs,
            )

            msg = response.choices[0].message
            content = msg.content or ""
            reasoning = self._extract_reasoning(msg)
            return content, reasoning
        except Exception as e:
            raise Exception(f"Cerebras API error: {str(e)}")

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        cerebras_kwargs = self._prepare_cerebras_args(model, **kwargs)
        try:
            image_detail = cerebras_kwargs.pop("image_detail", None)
            image_pixel_limit = cerebras_kwargs.pop("image_pixel_limit", None)
            fps = cerebras_kwargs.pop("fps", None)
            video_detail = cerebras_kwargs.pop("video_detail", None)
            max_frames = cerebras_kwargs.pop("max_frames", None)

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
                **cerebras_kwargs,
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
            error_msg = f"Cerebras Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"


cerebras_client = CerebrasClient()

