from typing import Dict, List, Tuple
import base64
import mimetypes
import os


class GeminiMessagesMixin:
    def _messages_to_contents_and_system(self, messages: List[Dict[str, str]]):
        system_parts: List[str] = []
        contents: List[Dict[str, object]] = []

        for m in messages:
            role = (m.get("role") or "").lower()
            content = m.get("content") or ""

            if role == "system":
                if content:
                    system_parts.append(content)
                continue

            # Gemini uses 'user' and 'model'
            if role == "assistant":
                g_role = "model"
            else:
                g_role = "user"

            thought_signatures = m.get("thought_signatures") or []
            if isinstance(content, list):
                parts = []
                for part in content:
                    if part.get("type") == "text":
                        item = {"text": part.get("text") or ""}
                        if part.get("thought_signature"):
                            item["thought_signature"] = part.get("thought_signature")
                        parts.append(item)
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "image/jpeg"
                                    with open(local_path, "rb") as image_file:
                                        parts.append(
                                            {
                                                "inline_data": {
                                                    "mime_type": mime_type,
                                                    "data": base64.b64encode(
                                                        image_file.read()
                                                    ).decode("utf-8"),
                                                }
                                            }
                                        )
                                else:
                                    print(f"[GeminiClient] Image not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading image {url}: {e}")
                    elif part.get("type") == "video_url":
                        url = part.get("video_url", {}).get("url")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "video/mp4"
                                    with open(local_path, "rb") as video_file:
                                        parts.append(
                                            {
                                                "inline_data": {
                                                    "mime_type": mime_type,
                                                    "data": base64.b64encode(
                                                        video_file.read()
                                                    ).decode("utf-8"),
                                                }
                                            }
                                        )
                                else:
                                    print(f"[GeminiClient] Video not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading video {url}: {e}")
                    elif part.get("type") == "audio_url":
                        url = part.get("audio_url", {}).get("url")
                        if url and url.startswith("/uploads/"):
                            try:
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                backend_dir = os.path.dirname(current_dir)
                                relative_path = url.lstrip("/")
                                local_path = os.path.join(backend_dir, relative_path)

                                if os.path.exists(local_path):
                                    mime_type, _ = mimetypes.guess_type(local_path)
                                    if not mime_type:
                                        mime_type = "audio/mpeg"
                                    with open(local_path, "rb") as audio_file:
                                        parts.append(
                                            {
                                                "inline_data": {
                                                    "mime_type": mime_type,
                                                    "data": base64.b64encode(
                                                        audio_file.read()
                                                    ).decode("utf-8"),
                                                }
                                            }
                                        )
                                else:
                                    print(f"[GeminiClient] Audio not found: {local_path}")
                            except Exception as e:
                                print(f"[GeminiClient] Error reading audio {url}: {e}")
                        elif url and url.startswith("http"):
                            # Gemini google-genai SDK might not support remote URLs in inline_data easily
                            # For now, we skip or could fetch + base64 if needed.
                            pass
                if thought_signatures and g_role == "model" and parts:
                    parts[0]["thought_signature"] = thought_signatures[0]
                contents.append({"role": g_role, "parts": parts})
            else:
                parts: List[Dict[str, object]] = [{"text": content}]
                if thought_signatures and g_role == "model":
                    parts[0]["thought_signature"] = thought_signatures[0]
                contents.append({"role": g_role, "parts": parts})

        system_instruction = "\n".join(system_parts).strip() or None
        return contents, system_instruction
