from typing import List, Dict, Optional, Tuple


class GeminiProvider:
    id = "gemini"
    name = "Gemini"
    description = "Google Gemini (google-genai SDK) models"
    supported = True

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        from .gemini_client import gemini_client
        return await gemini_client.chat(
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
        from .gemini_client import gemini_client
        async for chunk in gemini_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        from .gemini_client import gemini_client
        model_ids = gemini_client.list_models()

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
            name_parts = model_id.replace("/", " ").replace("-", " ").title().split()
            name = " ".join(name_parts)
            models.append(
                {
                    "id": model_id,
                    "name": name,
                    "provider": "gemini",
                    "description": f"{name}",
                }
            )
        return models


provider = GeminiProvider()
