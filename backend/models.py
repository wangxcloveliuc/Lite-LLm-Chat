"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Provider and Model schemas
class Provider(BaseModel):
    """Provider information"""

    id: str
    name: str
    description: str
    supported: bool = True


class Model(BaseModel):
    """Model information"""

    id: str
    name: str
    provider: str
    context_length: int | None = None
    description: str


# Chat message schemas
class MessageCreate(BaseModel):
    """Create a new message"""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class MessageResponse(BaseModel):
    """Message response"""

    id: int
    role: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    thought_process: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Chat session schemas
class SessionCreate(BaseModel):
    """Create a new chat session"""

    title: str = Field(..., min_length=1, max_length=255)
    provider: str
    model: str


class SessionUpdate(BaseModel):
    """Update chat session"""

    title: Optional[str] = None


class SessionResponse(BaseModel):
    """Chat session response"""

    id: int
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    """Detailed session response with messages"""

    messages: List[MessageResponse] = []


# Chat request/response schemas
class ChatRequest(BaseModel):
    """Chat completion request"""

    session_id: Optional[int] = None
    provider: str
    model: str
    messages: List[MessageCreate]
    message_provider: Optional[str] = None
    message_model: Optional[str] = None
    stream: bool = True
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    stop: Optional[List[str]] = None
    title: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat completion response (non-streaming)"""

    session_id: int
    message: MessageResponse
