from typing import List, Dict, Optional, Tuple


class DeepSeekProvider:
    id = "deepseek"
    name = "DeepSeek"
    description = "DeepSeek AI language models"
    supported = True

    async def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None) -> Tuple[str, str]:
        # Lazy import to avoid importing the OpenAI client at module import time
        from .deepseek_client import deepseek_client
        return await deepseek_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def stream_chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None):
        from .deepseek_client import deepseek_client
        async for chunk in deepseek_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    def list_models(self) -> List[Dict[str, object]]:
        return [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "provider": "deepseek",
                "description": "DeepSeek's flagship conversational model",
            },
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek Reasoner",
                "provider": "deepseek",
                "description": "DeepSeek's advanced reasoning model",
            },
        ]


# Module-level provider instance expected by the registry
provider = DeepSeekProvider()
