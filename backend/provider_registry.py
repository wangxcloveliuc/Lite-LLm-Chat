from typing import Dict, List, Optional, Tuple
import pkgutil
import importlib
from providers.base import LLMProvider


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
        except Exception as e:
            # Ignore problematic provider modules so registry remains usable
            import traceback
            print(f"[provider_registry] load {mod_name} failed: {e}")
            traceback.print_exc()
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


async def list_models(provider: Optional[str] = None) -> List[Dict[str, object]]:
    if provider:
        p = _PROVIDER_REGISTRY.get(provider)
        if not p:
            return []
        return await p.list_models()

    all_models: List[Dict[str, object]] = []
    for p in _PROVIDER_REGISTRY.values():
        models = await p.list_models()
        all_models.extend(models)
    return all_models


def get_provider(provider_id: str) -> Optional[LLMProvider]:
    return _PROVIDER_REGISTRY.get(provider_id)
