from typing import List, Dict, Optional, Tuple


class GroqProvider:
    id = "groq"
    name = "Groq"
    description = "Groq (OpenAI-compatible) language models"
    supported = True

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        from .groq_client import groq_client
        return await groq_client.chat(
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
        from .groq_client import groq_client
        async for chunk in groq_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        from .groq_client import groq_client
        model_ids = groq_client.list_models()

        # Fallback if API returns nothing (optional, but good for stability)
        if not model_ids:
            model_ids = [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
            ]

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
            # Filter out non-text models like whisper
            if "whisper" in model_id.lower():
                continue
                
            name_parts = model_id.replace("/", " ").replace("-", " ").title().split()
            name = " ".join(name_parts)
            models.append(
                {
                    "id": model_id,
                    "name": name,
                    "provider": "groq",
                    "description": f"{name}",
                }
            )
        return models


# Module-level provider instance expected by the registry
provider = GroqProvider()
