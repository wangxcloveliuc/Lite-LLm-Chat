"""
FastAPI Backend for Lite-LLM-Chat
"""
import asyncio

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from config import settings
from database import init_db, get_db, ChatSession, ChatMessage
from models import (
    Provider, Model, SessionCreate, SessionUpdate, SessionResponse,
    SessionDetailResponse, ChatRequest, ChatResponse, MessageResponse
)
from provider_registry import get_provider, list_models as registry_list_models, list_providers as registry_list_providers

# Lifespan handler to initialize resources on startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    init_db()
    yield
    # Optionally add shutdown/cleanup tasks here

# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend service for Lite-LLM-Chat with DeepSeek integration",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Provider Endpoints ====================

@app.get(f"{settings.api_prefix}/providers", response_model=List[Provider])
async def get_providers():
    """Get list of available LLM providers"""
    return [Provider(**p) for p in registry_list_providers()]


# ==================== Model Endpoints ====================

@app.get(f"{settings.api_prefix}/models", response_model=List[Model])
async def get_models(provider: str = None):
    """
    Get list of available models
    
    Args:
        provider: Optional filter by provider ID
    """
    return [Model(**m) for m in registry_list_models(provider=provider)]


# ==================== Session Endpoints ====================

@app.get(f"{settings.api_prefix}/sessions", response_model=List[SessionResponse])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of chat sessions
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    sessions = db.query(ChatSession)\
        .order_by(ChatSession.updated_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Add message count to each session
    result = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "title": session.title,
            "provider": session.provider,
            "model": session.model,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages)
        }
        result.append(SessionResponse(**session_dict))
    
    return result


@app.get(f"{settings.api_prefix}/sessions/{{session_id}}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific session including messages
    
    Args:
        session_id: The session ID
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Load ordered messages for the session (oldest -> newest)
    session_messages = (
        db.query(ChatMessage)
          .filter(ChatMessage.session_id == session_id)
          .order_by(ChatMessage.created_at.asc())
          .all()
    )
    
    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model=session.model,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session_messages),
        messages=[MessageResponse.model_validate(msg) for msg in session_messages]
    )


@app.post(f"{settings.api_prefix}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """
    Create a new chat session
    
    Args:
        session_data: Session creation data
    """
    session = ChatSession(
        title=session_data.title,
        provider=session_data.provider,
        model=session_data.model
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model=session.model,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )


@app.patch(f"{settings.api_prefix}/sessions/{{session_id}}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a chat session
    
    Args:
        session_id: The session ID
        session_data: Session update data
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    if session_data.title:
        session.title = session_data.title
    
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model=session.model,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session.messages)
    )


@app.delete(f"{settings.api_prefix}/sessions/{{session_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Delete a chat session
    
    Args:
        session_id: The session ID
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    db.delete(session)
    db.commit()


@app.delete(f"{settings.api_prefix}/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(db: Session = Depends(get_db)):
    """
    Delete all chat sessions
    """
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.commit()


# ==================== Chat Endpoints ====================

@app.post(f"{settings.api_prefix}/chat")
async def chat_completion(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat completion endpoint with streaming support
    
    Args:
        request: Chat request data
    """
    # Get or create session
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found"
            )
    else:
        # Create new session
        session = ChatSession(
            title=request.title or f"Chat {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            provider=request.provider,
            model=request.model
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    provider_id = request.message_provider or request.provider
    model_id = request.message_model or request.model
    provider_client = get_provider(provider_id)
    if not provider_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider_id}"
        )
    
    # Read existing session history (oldest -> newest)
    existing_messages = (
        db.query(ChatMessage)
          .filter(ChatMessage.session_id == session.id)
          .order_by(ChatMessage.created_at.asc())
          .all()
    )

    # Prepare incoming messages (only user/system).
    incoming_tuples = [(msg.role, msg.content) for msg in request.messages if msg.role in ("user", "system")]

    # Build API messages from full context (existing + deduped incoming) but DO NOT persist incoming messages yet
    api_messages = [{"role": m.role, "content": m.content} for m in existing_messages] + [{"role": r, "content": c} for r, c in incoming_tuples]

    # Keep in-memory ChatMessage objects for deduped incoming messages to persist later if the model call succeeds
    incoming_msg_objects = [
        ChatMessage(session_id=session.id, role=r, content=c, provider=provider_id, model=model_id)
        for r, c in incoming_tuples
    ]

    # Stream response
    if request.stream:
        async def generate():
            """Generator for streaming response"""
            # Send session ID first
            import json
            yield f"data: {json.dumps({'session_id': session.id})}\n\n"
            await asyncio.sleep(0)
            
            full_response = ""
            full_reasoning = ""
            failed = False
            try:
                async for chunk in provider_client.stream_chat(
                    model=model_id,
                    messages=api_messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    yield chunk
                    await asyncio.sleep(0)
                    # Extract content and reasoning for saving and detect errors
                    if chunk.startswith("data: "):
                        try:
                            data = json.loads(chunk[6:])
                            if "content" in data:
                                full_response += data["content"]
                            if "reasoning" in data:
                                full_reasoning += data["reasoning"]
                            if "error" in data:
                                failed = True
                                # stop processing further chunks
                                break
                        except:
                            pass
            except Exception as e:
                # Stream-level exception: notify client, do not persist
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return

            # If the stream signalled an error, do not persist
            if failed:
                return

            # Persist incoming messages and the assistant reply atomically, only if assistant produced content
            try:
                if full_response:
                    if incoming_msg_objects:
                        db.add_all(incoming_msg_objects)
                    assistant_message = ChatMessage(
                        session_id=session.id,
                        role="assistant",
                        content=full_response,
                        thought_process=full_reasoning if full_reasoning else None,
                        provider=provider_id,
                        model=model_id
                    )
                    db.add(assistant_message)
                    session.provider = provider_id
                    session.model = model_id
                    session.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as e:
                # If saving fails, notify client
                yield f"data: {json.dumps({'error': 'Failed to save messages'})}\n\n"        
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)
    
    # Non-streaming response
    else:
        try:
            response_content, reasoning_content = await provider_client.chat(
                model=model_id,
                messages=api_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Provider error: {str(e)}")
        
        # Persist incoming messages and assistant response atomically only if assistant produced content
        if not response_content:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Empty response from provider")
        try:
            if incoming_msg_objects:
                db.add_all(incoming_msg_objects)
            assistant_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=response_content,
                thought_process=reasoning_content if reasoning_content else None,
                provider=provider_id,
                model=model_id
            )
            db.add(assistant_message)
            session.provider = provider_id
            session.model = model_id
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(assistant_message)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save messages")
        
        return ChatResponse(
            session_id=session.id,
            message=MessageResponse.model_validate(assistant_message)
        )


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
