from typing import Dict, List, Optional, Tuple
import pkgutil
import importlib
import time
from providers.base import LLMProvider

try:
    from .config import settings
except (ImportError, ValueError):
    from config import settings


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


class ModelCacheEntry:
    def __init__(self, models: List[Dict[str, object]], timestamp: float):
        self.models = models
        self.timestamp = timestamp


_MODEL_CACHE: Dict[str, ModelCacheEntry] = {}


def _is_cache_valid(entry: ModelCacheEntry) -> bool:
    if settings.model_cache_ttl <= 0:
        return False
    return time.time() - entry.timestamp < settings.model_cache_ttl


def _get_cached_models(provider_id: Optional[str]) -> Optional[List[Dict[str, object]]]:
    if provider_id is None:
        return None
    entry = _MODEL_CACHE.get(provider_id)
    if entry and _is_cache_valid(entry):
        return entry.models
    return None


def _set_cached_models(provider_id: str, models: List[Dict[str, object]]) -> None:
    if settings.model_cache_ttl > 0:
        _MODEL_CACHE[provider_id] = ModelCacheEntry(models, time.time())


def _clear_cache(provider_id: Optional[str] = None) -> None:
    if provider_id:
        _MODEL_CACHE.pop(provider_id, None)
    else:
        _MODEL_CACHE.clear()


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
        cached = _get_cached_models(provider)
        if cached is not None:
            return cached

        p = _PROVIDER_REGISTRY.get(provider)
        if not p:
            return []
        models = await p.list_models()
        _set_cached_models(provider, models)
        print( f"[provider_registry] Fetched and cached models for provider '{provider}'")
        print(models)
        return models

    all_models: List[Dict[str, object]] = []
    for provider_id, p in _PROVIDER_REGISTRY.items():
        cached = _get_cached_models(provider_id)
        if cached is not None:
            all_models.extend(cached)
        else:
            models = await p.list_models()
            _set_cached_models(provider_id, models)
            all_models.extend(models)
    return all_models


def get_provider(provider_id: str) -> Optional[LLMProvider]:
    return _PROVIDER_REGISTRY.get(provider_id)


async def refresh_models_cache(provider: Optional[str] = None) -> None:
    if provider:
        _clear_cache(provider)
        await list_models(provider)
    else:
        _clear_cache()
        await list_models()
