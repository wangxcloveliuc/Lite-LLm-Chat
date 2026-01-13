"""
FastAPI Backend for Lite-LLM-Chat
"""

import asyncio
import os
import uuid
import shutil
import json
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager

from config import settings
from database import init_db, get_db, ChatSession, ChatMessage
from models import (
    Provider,
    Model,
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
    ChatRequest,
    ChatResponse,
    MessageResponse,
)
from provider_registry import (
    get_provider,
    list_models as registry_list_models,
    list_providers as registry_list_providers,
)


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
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount the uploads directory to serve static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


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
    return [Model(**m) for m in await registry_list_models(provider=provider)]


# ==================== Upload Endpoints ====================


@app.post(f"{settings.api_prefix}/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (image) and return its URL
    """
    # Create unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )

    # Return URL (relative to base URL)
    return {"url": f"/uploads/{unique_filename}"}


# ==================== Session Endpoints ====================


@app.get(f"{settings.api_prefix}/sessions", response_model=List[SessionResponse])
async def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of chat sessions

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

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
            "message_count": len(session.messages),
        }
        result.append(SessionResponse(**session_dict))

    return result


@app.get(
    f"{settings.api_prefix}/sessions/{{session_id}}",
    response_model=SessionDetailResponse,
)
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
            detail=f"Session {session_id} not found",
        )

    # Load ordered messages for the session (oldest -> newest)
    session_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    # Pre-process messages to handle SQLite JSON columns
    processed_messages = []
    for msg in session_messages:
        msg_dict = {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "provider": msg.provider,
            "model": msg.model,
            "thought_process": msg.thought_process,
            "created_at": msg.created_at,
            "images": msg.images if not isinstance(msg.images, str) else (json.loads(msg.images) if msg.images else []),
            "videos": msg.videos if not isinstance(msg.videos, str) else (json.loads(msg.videos) if msg.videos else []),
        }
        processed_messages.append(MessageResponse(**msg_dict))

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        provider=session.provider,
        model=session.model,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session_messages),
        messages=processed_messages,
    )


@app.post(
    f"{settings.api_prefix}/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """
    Create a new chat session

    Args:
        session_data: Session creation data
    """
    session = ChatSession(
        title=session_data.title,
        provider=session_data.provider,
        model=session_data.model,
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
        message_count=0,
    )


@app.patch(
    f"{settings.api_prefix}/sessions/{{session_id}}", response_model=SessionResponse
)
async def update_session(
    session_id: int, session_data: SessionUpdate, db: Session = Depends(get_db)
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
            detail=f"Session {session_id} not found",
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
        message_count=len(session.messages),
    )


@app.delete(
    f"{settings.api_prefix}/sessions/{{session_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
)
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
            detail=f"Session {session_id} not found",
        )

    db.delete(session)
    db.commit()


@app.delete(
    f"{settings.api_prefix}/sessions/{{session_id}}/truncate/{{message_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def truncate_session(
    session_id: int, message_id: int, db: Session = Depends(get_db)
):
    """
    Delete all messages in a session starting from a specific message ID (inclusive)

    Args:
        session_id: The session ID
        message_id: The ID of the message from which to start deleting
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id, ChatMessage.id >= message_id
    ).delete()

    session.updated_at = datetime.now(timezone.utc)
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
async def chat_completion(
    chat_request: ChatRequest, request: Request, db: Session = Depends(get_db)
):
    """
    Chat completion endpoint with streaming support

    Args:
        request: Chat request data
    """
    # Get or create session
    if chat_request.session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == chat_request.session_id)
            .first()
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {chat_request.session_id} not found",
            )
    else:
        # Create new session
        session = ChatSession(
            title=chat_request.title
            or f"Chat {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            provider=chat_request.provider,
            model=chat_request.model,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    provider_id = chat_request.message_provider or chat_request.provider
    model_id = chat_request.message_model or chat_request.model
    provider_client = get_provider(provider_id)
    if not provider_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider_id}",
        )

    # Read existing session history (oldest -> newest)
    existing_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    # Helper to ensure images is a list (handles SQLite JSON as string)
    def ensure_list(data):
        if data is None:
            return None
        if isinstance(data, str):
            try:
                return json.loads(data)
            except:
                return [data] if data else []
        return data

    # Prepare incoming messages (only user/system).
    # Each tuple is (role, content, images, videos, audios)
    incoming_data = [
        (msg.role, msg.content, ensure_list(msg.images), ensure_list(msg.videos), ensure_list(msg.audios))
        for msg in chat_request.messages
        if msg.role in ("user", "system")
    ]

    # Helper to format content for API (multi-modal support)
    def format_api_content(
        content: str, 
        images: Optional[List[str]], 
        videos: Optional[List[str]] = None,
        audios: Optional[List[str]] = None
    ):
        images = ensure_list(images)
        videos = ensure_list(videos)
        audios = ensure_list(audios)
        if not images and not videos and not audios:
            return content
        
        parts = [{"type": "text", "text": content}]
        if images:
            for img_url in images:
                img_part = {
                    "type": "image_url",
                    "image_url": {"url": img_url}
                }
                parts.append(img_part)
        if videos:
            for video_url in videos:
                video_part = {
                    "type": "video_url",
                    "video_url": {"url": video_url}
                }
                parts.append(video_part)
        if audios:
            for audio_url in audios:
                audio_part = {
                    "type": "audio_url",
                    "audio_url": {"url": audio_url}
                }
                parts.append(audio_part)
        return parts

    # Build API messages from full context (existing + deduped incoming) but DO NOT persist incoming messages yet
    api_messages = [
        {"role": m.role, "content": format_api_content(m.content, m.images, getattr(m, 'videos', None), getattr(m, 'audios', None))} 
        for m in existing_messages
    ] + [
        {"role": r, "content": format_api_content(c, i, v, a)} 
        for r, c, i, v, a in incoming_data
    ]

    # Add system prompt at the beginning if provided
    if chat_request.system_prompt:
        api_messages = [
            {"role": "system", "content": chat_request.system_prompt}
        ] + api_messages

    # Keep in-memory ChatMessage objects for deduped incoming messages
    incoming_msg_objects = [
        ChatMessage(
            session_id=session.id,
            role=r,
            content=c,
            images=i, # Pass list directly, SQLAlchemy JSON type handles it
            videos=v,
            audios=a,
            provider=provider_id,
            model=model_id,
        )
        for r, c, i, v, a in incoming_data
    ]

    # Persist incoming messages immediately so they aren't lost if the model call fails
    if incoming_msg_objects:
        db.add_all(incoming_msg_objects)
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

    # Stream response
    if chat_request.stream:

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
                # Prepare provider-specific arguments, filtering out None values for optional extended settings
                provider_kwargs = {
                    "temperature": chat_request.temperature,
                    "max_tokens": chat_request.max_tokens,
                    "frequency_penalty": chat_request.frequency_penalty,
                    "presence_penalty": chat_request.presence_penalty,
                    "top_p": chat_request.top_p,
                    "stop": chat_request.stop,
                }
                
                if chat_request.thinking is not None:
                    provider_kwargs["thinking"] = chat_request.thinking
                if chat_request.reasoning_effort is not None:
                    provider_kwargs["reasoning_effort"] = chat_request.reasoning_effort
                if chat_request.max_completion_tokens is not None:
                    provider_kwargs["max_completion_tokens"] = chat_request.max_completion_tokens
                if chat_request.enable_thinking is not None:
                    provider_kwargs["enable_thinking"] = chat_request.enable_thinking
                if chat_request.thinking_budget is not None:
                    provider_kwargs["thinking_budget"] = chat_request.thinking_budget
                if chat_request.min_p is not None:
                    provider_kwargs["min_p"] = chat_request.min_p
                if chat_request.top_k is not None:
                    provider_kwargs["top_k"] = chat_request.top_k
                if chat_request.image_detail is not None:
                    provider_kwargs["image_detail"] = chat_request.image_detail
                if chat_request.image_pixel_limit is not None:
                    provider_kwargs["image_pixel_limit"] = chat_request.image_pixel_limit.model_dump(exclude_none=True)
                if chat_request.fps is not None:
                    provider_kwargs["fps"] = chat_request.fps
                if chat_request.video_detail is not None:
                    provider_kwargs["video_detail"] = chat_request.video_detail
                if chat_request.max_frames is not None:
                    provider_kwargs["max_frames"] = chat_request.max_frames

                stream = provider_client.stream_chat(
                    model=model_id,
                    messages=api_messages,
                    **provider_kwargs
                )

                client_gone = False
                next_chunk_task = None
                try:
                    next_chunk_task = asyncio.ensure_future(stream.__anext__())
                    while True:
                        # Poll for client disconnects while waiting for provider chunks
                        if await request.is_disconnected():
                            client_gone = True
                            break

                        done, _ = await asyncio.wait({next_chunk_task}, timeout=0.5)
                        if not done:
                            continue

                        try:
                            chunk = next_chunk_task.result()
                        except StopAsyncIteration:
                            break
                        except asyncio.CancelledError:
                            # client cancelled; stop processing and do not persist
                            return

                        yield chunk
                        await asyncio.sleep(0)

                        next_chunk_task = asyncio.ensure_future(stream.__anext__())
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
                finally:
                    if next_chunk_task is not None and not next_chunk_task.done():
                        next_chunk_task.cancel()

                    # Ensure provider stream is closed when client disconnects or loop ends
                    aclose = getattr(stream, "aclose", None)
                    if callable(aclose):
                        try:
                            await aclose()
                        except Exception:
                            pass

                if client_gone:
                    return

            except Exception as e:
                # Stream-level exception: notify client, do not persist
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return

            # If the stream signalled an error, do not persist assistant reply
            if failed:
                return

            # Persist the assistant reply, only if assistant produced content
            try:
                if full_response:
                    assistant_message = ChatMessage(
                        session_id=session.id,
                        role="assistant",
                        content=full_response,
                        thought_process=full_reasoning if full_reasoning else None,
                        provider=provider_id,
                        model=model_id,
                    )
                    db.add(assistant_message)
                    session.provider = provider_id
                    session.model = model_id
                    session.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as e:
                # If saving fails, notify client
                yield f"data: {json.dumps({'error': 'Failed to save assistant response'})}\n\n"

        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(
            generate(), media_type="text/event-stream", headers=headers
        )

    # Non-streaming response
    else:
        try:
            # Prepare provider-specific arguments, filtering out None values for optional extended settings
            provider_kwargs = {
                "temperature": chat_request.temperature,
                "max_tokens": chat_request.max_tokens,
                "frequency_penalty": chat_request.frequency_penalty,
                "presence_penalty": chat_request.presence_penalty,
                "top_p": chat_request.top_p,
                "stop": chat_request.stop,
            }
            
            if chat_request.thinking is not None:
                provider_kwargs["thinking"] = chat_request.thinking
            if chat_request.reasoning_effort is not None:
                provider_kwargs["reasoning_effort"] = chat_request.reasoning_effort
            if chat_request.max_completion_tokens is not None:
                provider_kwargs["max_completion_tokens"] = chat_request.max_completion_tokens
            if chat_request.enable_thinking is not None:
                provider_kwargs["enable_thinking"] = chat_request.enable_thinking
            if chat_request.thinking_budget is not None:
                provider_kwargs["thinking_budget"] = chat_request.thinking_budget
            if chat_request.min_p is not None:
                provider_kwargs["min_p"] = chat_request.min_p
            if chat_request.top_k is not None:
                provider_kwargs["top_k"] = chat_request.top_k
            if chat_request.image_detail is not None:
                provider_kwargs["image_detail"] = chat_request.image_detail
            if chat_request.image_pixel_limit is not None:
                provider_kwargs["image_pixel_limit"] = chat_request.image_pixel_limit.model_dump(exclude_none=True)
            if chat_request.fps is not None:
                provider_kwargs["fps"] = chat_request.fps
            if chat_request.video_detail is not None:
                provider_kwargs["video_detail"] = chat_request.video_detail
            if chat_request.max_frames is not None:
                provider_kwargs["max_frames"] = chat_request.max_frames

            response_content, reasoning_content = await provider_client.chat(
                model=model_id,
                messages=api_messages,
                **provider_kwargs
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Provider error: {str(e)}",
            )

        # Persist assistant response only if assistant produced content
        if not response_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Empty response from provider",
            )
        try:
            assistant_message = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=response_content,
                thought_process=reasoning_content if reasoning_content else None,
                provider=provider_id,
                model=model_id,
            )
            db.add(assistant_message)
            session.provider = provider_id
            session.model = model_id
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(assistant_message)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save assistant message",
            )

        return ChatResponse(
            session_id=session.id,
            message=MessageResponse.model_validate(assistant_message),
        )


# ==================== Health Check ====================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
