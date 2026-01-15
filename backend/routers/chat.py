import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from config import settings
from database import ChatMessage, ChatSession, get_db
from models import ChatRequest, ChatResponse, MessageResponse
from provider_registry import get_provider
from .chat_helpers import (
    _build_provider_kwargs,
    _ensure_list,
    _format_api_content,
    _localize_markdown_images,
    _localize_streaming_content,
)


router = APIRouter()


@router.post(f"{settings.api_prefix}/chat")
async def chat_completion(
    chat_request: ChatRequest, request: Request, db: Session = Depends(get_db)
):
    """
    Chat completion endpoint with streaming support

    Args:
        request: Chat request data
    """
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

    existing_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    incoming_data = [
        (
            msg.role,
            msg.content,
            _ensure_list(msg.images),
            _ensure_list(msg.videos),
            _ensure_list(msg.audios),
        )
        for msg in chat_request.messages
        if msg.role in ("user", "system")
    ]

    api_messages = [
        {
            "role": m.role,
            "content": _format_api_content(
                m.content,
                m.images,
                getattr(m, "videos", None),
                getattr(m, "audios", None),
            ),
        }
        for m in existing_messages
    ] + [
        {"role": r, "content": _format_api_content(c, i, v, a)}
        for r, c, i, v, a in incoming_data
    ]

    if chat_request.system_prompt:
        api_messages = (
            [{"role": "system", "content": chat_request.system_prompt}] + api_messages
        )

    incoming_msg_objects = [
        ChatMessage(
            session_id=session.id,
            role=r,
            content=c,
            images=i,
            videos=v,
            audios=a,
            provider=provider_id,
            model=model_id,
        )
        for r, c, i, v, a in incoming_data
    ]

    if incoming_msg_objects:
        db.add_all(incoming_msg_objects)
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

    if chat_request.stream:

        async def generate():
            yield f"data: {json.dumps({'session_id': session.id})}\n\n"
            await asyncio.sleep(0)

            full_response = ""
            full_reasoning = ""
            failed = False
            try:
                provider_kwargs = _build_provider_kwargs(chat_request)

                stream = provider_client.stream_chat(
                    model=model_id,
                    messages=api_messages,
                    **provider_kwargs,
                )

                client_gone = False
                next_chunk_task = None
                try:
                    next_chunk_task = asyncio.ensure_future(stream.__anext__())
                    while True:
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
                            return

                        try:
                            chunk_data = json.loads(chunk[6:])
                            if "content" in chunk_data:
                                content_val = chunk_data["content"]
                                content_val, modified = await _localize_streaming_content(content_val)
                                if modified:
                                    chunk_data["content"] = content_val
                                    chunk = f"data: {json.dumps(chunk_data)}\n\n"

                                full_response += content_val

                            if "reasoning" in chunk_data:
                                full_reasoning += chunk_data["reasoning"]
                            if "error" in chunk_data:
                                failed = True
                                yield chunk  # Send the error chunk
                                break
                        except Exception as e:
                            print(f"Error processing chunk: {e}")
                            pass

                        yield chunk
                        await asyncio.sleep(0)
                        next_chunk_task = asyncio.ensure_future(stream.__anext__())
                finally:
                    if next_chunk_task is not None and not next_chunk_task.done():
                        next_chunk_task.cancel()

                    aclose = getattr(stream, "aclose", None)
                    if callable(aclose):
                        try:
                            await aclose()
                        except Exception:
                            pass

                if client_gone:
                    return

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return

            if failed:
                return

            try:
                if full_response:
                    full_response, _ = await _localize_markdown_images(full_response)

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
                print(f"Error saving assistant response: {e}")
                yield f"data: {json.dumps({'error': 'Failed to save assistant response'})}\n\n"

        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)

    try:
        provider_kwargs = _build_provider_kwargs(chat_request)

        # Handle Seedream non-streaming if needed (though UI usually uses stream)
        response_content, reasoning_content = await provider_client.chat(
            model=model_id,
            messages=api_messages,
            **provider_kwargs,
        )

        # Process images for non-streaming response
        response_content, _ = await _localize_markdown_images(response_content)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider error: {str(e)}",
        )

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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save assistant message",
        )

    return ChatResponse(
        session_id=session.id,
        message=MessageResponse.model_validate(assistant_message),
    )
