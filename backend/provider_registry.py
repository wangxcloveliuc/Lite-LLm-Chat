from typing import Dict, List, Optional, Tuple

from deepseek_client import deepseek_client


class LLMProvider:
    id: str
    name: str
    description: str
    supported: bool

    async def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None) -> Tuple[str, str]:
        raise NotImplementedError()

    async def stream_chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None):
        raise NotImplementedError()

    def list_models(self) -> List[Dict[str, object]]:
        raise NotImplementedError()


class DeepSeekProvider(LLMProvider):
    id = "deepseek"
    name = "DeepSeek"
    description = "DeepSeek AI language models"
    supported = True

    async def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None) -> str:
        return await deepseek_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def stream_chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 1, max_tokens: Optional[int] = None):
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


_PROVIDER_REGISTRY: Dict[str, LLMProvider] = {
    DeepSeekProvider.id: DeepSeekProvider(),
}


def list_providers() -> List[Dict[str, object]]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "supported": p.supported,
        }
        for p in _PROVIDER_REGISTRY.values()
    ]


def list_models(provider: Optional[str] = None) -> List[Dict[str, object]]:
    if provider:
        p = _PROVIDER_REGISTRY.get(provider)
        if not p:
            return []
        return p.list_models()

    all_models: List[Dict[str, object]] = []
    for p in _PROVIDER_REGISTRY.values():
        all_models.extend(p.list_models())
    return all_models


def get_provider(provider_id: str) -> Optional[LLMProvider]:
    return _PROVIDER_REGISTRY.get(provider_id)
