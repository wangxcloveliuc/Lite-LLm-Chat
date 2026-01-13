"""
FastAPI app factory for Lite-LLM-Chat
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from routers.chat import router as chat_router
from routers.health import router as health_router
from routers.models import router as models_router
from routers.providers import router as providers_router
from routers.sessions import router as sessions_router
from routers.upload import get_router as get_upload_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend service for Lite-LLM-Chat with DeepSeek integration",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    app.include_router(providers_router)
    app.include_router(models_router)
    app.include_router(get_upload_router(upload_dir))
    app.include_router(sessions_router)
    app.include_router(chat_router)
    app.include_router(health_router)

    return app
