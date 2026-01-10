from typing import List, Dict, Optional, Tuple


class MistralProvider:
    id = "mistral"
    name = "Mistral"
    description = "Mistral (OpenAI-compatible) language models"
    supported = True

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        from .mistral_client import mistral_client
        return await mistral_client.chat(
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
        from .mistral_client import mistral_client
        async for chunk in mistral_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        from .mistral_client import mistral_client
        model_ids = mistral_client.list_models()

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
            name_parts = model_id.replace("/", " ").replace("-", " ").title().split()
            name = " ".join(name_parts)
            models.append(
                {
                    "id": model_id,
                    "name": name,
                    "provider": "mistral",
                    "description": f"{name}",
                }
            )
        return models


provider = MistralProvider()
