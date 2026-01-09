from typing import Dict, List, Optional, Tuple
import pkgutil
import importlib


# Provider adapter modules should expose a module-level `provider` instance
# which the registry will discover dynamically.



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


def _discover_providers() -> Dict[str, LLMProvider]:
    registry: Dict[str, LLMProvider] = {}
    
    # Try to import the providers package relatively or absolutely
    providers_pkg = None
    try:
        from . import providers as providers_pkg
    except (ImportError, ValueError):
        try:
            import providers as providers_pkg
        except ImportError:
            return registry

    if not providers_pkg:
        return registry

    for finder, name, ispkg in pkgutil.iter_modules(providers_pkg.__path__):
        try:
            # Import modules relative to the providers package name
            mod_name = f"{providers_pkg.__name__}.{name}"
            mod = importlib.import_module(mod_name)
            p = getattr(mod, "provider", None)
            if p and getattr(p, "id", None):
                registry[p.id] = p
        except Exception:
            # Ignore problematic provider modules so registry remains usable
            continue

    return registry


_PROVIDER_REGISTRY: Dict[str, LLMProvider] = _discover_providers()


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
