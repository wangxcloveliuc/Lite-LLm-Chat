import asyncio
import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from config import settings
from database import ChatMessage, ChatSession, get_db
from models import ChatRequest, ChatResponse, MessageResponse
from provider_registry import get_provider


router = APIRouter()


def _ensure_list(data):
    if data is None:
        return None
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            return [data] if data else []
    return data


def _format_api_content(
    content: str,
    images: Optional[List[str]],
    videos: Optional[List[str]] = None,
    audios: Optional[List[str]] = None,
):
    images = _ensure_list(images)
    videos = _ensure_list(videos)
    audios = _ensure_list(audios)
    if not images and not videos and not audios:
        return content

    parts = [{"type": "text", "text": content}]
    if images:
        for img_url in images:
            parts.append({"type": "image_url", "image_url": {"url": img_url}})
    if videos:
        for video_url in videos:
            parts.append({"type": "video_url", "video_url": {"url": video_url}})
    if audios:
        for audio_url in audios:
            parts.append({"type": "audio_url", "audio_url": {"url": audio_url}})
    return parts


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
                if chat_request.disable_reasoning is not None:
                    provider_kwargs["disable_reasoning"] = chat_request.disable_reasoning
                if chat_request.reasoning_format is not None:
                    provider_kwargs["reasoning_format"] = chat_request.reasoning_format
                if chat_request.include_reasoning is not None:
                    provider_kwargs["include_reasoning"] = chat_request.include_reasoning
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
                if chat_request.safe_prompt is not None:
                    provider_kwargs["safe_prompt"] = chat_request.safe_prompt
                if chat_request.random_seed is not None:
                    provider_kwargs["random_seed"] = chat_request.random_seed
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

                        yield chunk
                        await asyncio.sleep(0)

                        next_chunk_task = asyncio.ensure_future(stream.__anext__())

                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                if "content" in data:
                                    full_response += data["content"]
                                if "reasoning" in data:
                                    full_reasoning += data["reasoning"]
                                if "error" in data:
                                    failed = True
                                    break
                            except Exception:
                                pass
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
            except Exception:
                yield f"data: {json.dumps({'error': 'Failed to save assistant response'})}\n\n"

        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)

    try:
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
        if chat_request.disable_reasoning is not None:
            provider_kwargs["disable_reasoning"] = chat_request.disable_reasoning
        if chat_request.reasoning_format is not None:
            provider_kwargs["reasoning_format"] = chat_request.reasoning_format
        if chat_request.include_reasoning is not None:
            provider_kwargs["include_reasoning"] = chat_request.include_reasoning
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
        if chat_request.safe_prompt is not None:
            provider_kwargs["safe_prompt"] = chat_request.safe_prompt
        if chat_request.random_seed is not None:
            provider_kwargs["random_seed"] = chat_request.random_seed
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
            **provider_kwargs,
        )
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
