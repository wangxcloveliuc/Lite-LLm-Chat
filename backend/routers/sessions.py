import json
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from database import get_db, ChatSession, ChatMessage
from models import SessionCreate, SessionUpdate, SessionResponse, SessionDetailResponse, MessageResponse


router = APIRouter()


@router.get(f"{settings.api_prefix}/sessions", response_model=List[SessionResponse])
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


@router.get(
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

    session_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

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


@router.post(
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


@router.patch(
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


@router.delete(
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


@router.delete(
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


@router.delete(f"{settings.api_prefix}/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(db: Session = Depends(get_db)):
    """
    Delete all chat sessions
    """
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.commit()
