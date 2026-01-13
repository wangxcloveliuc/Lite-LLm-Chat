from fastapi import APIRouter
from typing import List

from config import settings
from models import Model
from provider_registry import list_models as registry_list_models


router = APIRouter()


@router.get(f"{settings.api_prefix}/models", response_model=List[Model])
async def get_models(provider: str = None):
    """
    Get list of available models

    Args:
        provider: Optional filter by provider ID
    """
    return [Model(**m) for m in await registry_list_models(provider=provider)]
