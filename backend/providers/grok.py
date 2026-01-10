from typing import List, Dict, Optional, Tuple


class GrokProvider:
    id = "grok"
    name = "Grok"
    description = "Grok (xAI, OpenAI-compatible) language models"
    supported = True

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        from .grok_client import grok_client
        return await grok_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ):
        from .grok_client import grok_client
        async for chunk in grok_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        from .grok_client import grok_client
        model_ids = grok_client.list_models()

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
            name_parts = model_id.replace("/", " ").replace("-", " ").title().split()
            name = " ".join(name_parts)
            models.append(
                {
                    "id": model_id,
                    "name": name,
                    "provider": "grok",
                    "description": f"{name}",
                }
            )
        return models


provider = GrokProvider()
