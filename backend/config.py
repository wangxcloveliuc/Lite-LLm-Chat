"""
Configuration settings for the FastAPI backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Lite-LLM-Chat Backend"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./chat_history.db"
    
    # DeepSeek API
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"

    # Doubao (Volcengine Ark) API
    doubao_api_key: Optional[str] = None
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
