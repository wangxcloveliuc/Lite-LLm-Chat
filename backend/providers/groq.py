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

    def list_models(self) -> List[Dict[str, object]]:
        model_ids = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "moonshotai/kimi-k2-instruct",
            "moonshotai/kimi-k2-instruct-0905",
            "qwen/qwen3-32b",
        ]

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
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
