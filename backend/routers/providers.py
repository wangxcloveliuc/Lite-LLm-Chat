from fastapi import APIRouter
from typing import List

from config import settings
from models import Provider
from provider_registry import list_providers as registry_list_providers


router = APIRouter()


@router.get(f"{settings.api_prefix}/providers", response_model=List[Provider])
async def get_providers():
    """Get list of available LLM providers"""
    return [Provider(**p) for p in registry_list_providers()]
