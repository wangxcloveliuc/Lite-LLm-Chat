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

    http_proxy: Optional[str] = None
    # Outbound request timeout (seconds) for LLM provider calls
    provider_timeout: float = 20.0
    
    # Database
    database_url: str = "sqlite:///./chat_history.db"
    
    # DeepSeek API
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"

    # Doubao (Volcengine Ark) API
    doubao_api_key: Optional[str] = None
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

    # SiliconFlow (OpenAI-compatible) API
    siliconflow_api_key: Optional[str] = None
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"

    # Groq (OpenAI-compatible) API
    groq_api_key: Optional[str] = None
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Mistral (OpenAI-compatible) API
    mistral_api_key: Optional[str] = None
    mistral_base_url: str = "https://api.mistral.ai/v1"

    # Grok (xAI, OpenAI-compatible) API
    grok_api_key: Optional[str] = None
    grok_base_url: str = "https://api.x.ai/v1"

    # OpenRouter (OpenAI-compatible) API
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_http_referer: Optional[str] = None
    openrouter_x_title: Optional[str] = None

    # Gemini (Google GenAI SDK)
    gemini_api_key: Optional[str] = None

    # Cerebras (OpenAI-compatible) API
    cerebras_api_key: Optional[str] = None
    cerebras_base_url: str = "https://api.cerebras.ai/v1"

    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
