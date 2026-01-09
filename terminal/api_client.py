"""
API Client for Lite-LLM-Chat Backend
Handles all HTTP communication with the backend API
"""
import aiohttp
import json
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Provider:
    """Provider information"""
    id: str
    name: str
    description: str
    supported: bool = True


@dataclass
class Model:
    """Model information"""
    id: str
    name: str
    provider: str
    description: str
    context_length: Optional[int] = None


@dataclass
class Message:
    """Chat message"""
    role: str
    content: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    thought_process: Optional[str] = None


@dataclass
class Session:
    """Chat session"""
    id: int
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    messages: List[Message] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class APIClient:
    """Client for communicating with Lite-LLM-Chat backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _url(self, path: str) -> str:
        """Construct full URL for API endpoint"""
        return f"{self.base_url}{self.api_prefix}{path}"
    
    async def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            async with self.session.get(f"{self.base_url}/health") as resp:
                return resp.status == 200
        except:
            return False
    
    # ==================== Provider Methods ====================
    
    async def get_providers(self) -> List[Provider]:
        """Get list of available providers"""
        async with self.session.get(self._url("/providers")) as resp:
            if resp.status == 200:
                data = await resp.json()
                return [Provider(**p) for p in data]
            return []
    
    # ==================== Model Methods ====================
    
    async def get_models(self, provider: Optional[str] = None) -> List[Model]:
        """Get list of available models, optionally filtered by provider"""
        params = {}
        if provider:
            params['provider'] = provider
        
        async with self.session.get(self._url("/models"), params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return [Model(**m) for m in data]
            return []
    
    # ==================== Session Methods ====================
    
    async def get_sessions(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """Get list of chat sessions"""
        params = {'skip': skip, 'limit': limit}
        async with self.session.get(self._url("/sessions"), params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                sessions = []
                for s in data:
                    sessions.append(Session(
                        id=s['id'],
                        title=s['title'],
                        provider=s['provider'],
                        model=s['model'],
                        created_at=datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(s['updated_at'].replace('Z', '+00:00')),
                        message_count=s.get('message_count', 0)
                    ))
                return sessions
            return []
    
    async def get_session(self, session_id: int) -> Optional[Session]:
        """Get detailed session with messages"""
        async with self.session.get(self._url(f"/sessions/{session_id}")) as resp:
            if resp.status == 200:
                data = await resp.json()
                messages = []
                for m in data.get('messages', []):
                    messages.append(Message(
                        id=m['id'],
                        role=m['role'],
                        content=m['content'],
                        thought_process=m.get('thought_process'),
                        provider=m.get('provider'),
                        model=m.get('model'),
                        created_at=datetime.fromisoformat(m['created_at'].replace('Z', '+00:00'))
                    ))
                
                return Session(
                    id=data['id'],
                    title=data['title'],
                    provider=data['provider'],
                    model=data['model'],
                    created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')),
                    message_count=data.get('message_count', 0),
                    messages=messages
                )
            return None
    
    async def create_session(self, title: str, provider: str, model: str) -> Optional[Session]:
        """Create a new chat session"""
        payload = {
            'title': title,
            'provider': provider,
            'model': model
        }
        async with self.session.post(self._url("/sessions"), json=payload) as resp:
            if resp.status == 201:
                data = await resp.json()
                return Session(
                    id=data['id'],
                    title=data['title'],
                    provider=data['provider'],
                    model=data['model'],
                    created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')),
                    message_count=0
                )
            return None
    
    async def update_session(self, session_id: int, title: str) -> bool:
        """Update session title"""
        payload = {'title': title}
        async with self.session.patch(self._url(f"/sessions/{session_id}"), json=payload) as resp:
            return resp.status == 200
    
    async def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        async with self.session.delete(self._url(f"/sessions/{session_id}")) as resp:
            return resp.status == 204
    
    async def delete_all_sessions(self) -> bool:
        """Delete all sessions"""
        async with self.session.delete(self._url("/sessions")) as resp:
            return resp.status == 204
    
    # ==================== Chat Methods ====================
    
    async def chat(
        self,
        messages: List[Message],
        provider: str,
        model: str,
        session_id: Optional[int] = None,
        message_provider: Optional[str] = None,
        message_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        title: Optional[str] = None
    ) -> Optional[Dict]:
        """Non-streaming chat completion"""
        payload = {
            'provider': provider,
            'model': model,
            'messages': [{'role': m.role, 'content': m.content} for m in messages],
            'stream': False,
            'temperature': temperature
        }
        
        if session_id:
            payload['session_id'] = session_id
        if message_provider:
            payload['message_provider'] = message_provider
        if message_model:
            payload['message_model'] = message_model
        if max_tokens:
            payload['max_tokens'] = max_tokens
        if title:
            payload['title'] = title
        
        async with self.session.post(self._url("/chat"), json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
    
    async def chat_stream(
        self,
        messages: List[Message],
        provider: str,
        model: str,
        session_id: Optional[int] = None,
        message_provider: Optional[str] = None,
        message_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        title: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """Streaming chat completion"""
        payload = {
            'provider': provider,
            'model': model,
            'messages': [{'role': m.role, 'content': m.content} for m in messages],
            'stream': True,
            'temperature': temperature
        }
        
        if session_id:
            payload['session_id'] = session_id
        if message_provider:
            payload['message_provider'] = message_provider
        if message_model:
            payload['message_model'] = message_model
        if max_tokens:
            payload['max_tokens'] = max_tokens
        if title:
            payload['title'] = title
        
        async with self.session.post(self._url("/chat"), json=payload) as resp:
            if resp.status == 200:
                buffer = ""
                # Use a small chunk size to avoid client-side buffering delaying SSE processing.
                async for chunk in resp.content.iter_chunked(1024):
                    if not chunk:
                        continue
                    buffer += chunk.decode('utf-8', errors='ignore')

                    while "\n" in buffer:
                        raw_line, buffer = buffer.split("\n", 1)
                        line = raw_line.rstrip("\r")
                        if not line:
                            continue
                        if not line.startswith('data:'):
                            continue

                        data_str = line[5:].lstrip()
                        if not data_str:
                            continue
                        if data_str == "[DONE]":
                            return
                        try:
                            data = json.loads(data_str)
                            yield data
                        except json.JSONDecodeError:
                            continue
