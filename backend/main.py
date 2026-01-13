"""
FastAPI Backend for Lite-LLM-Chat
"""

from app_factory import create_app
from config import settings


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
