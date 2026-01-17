from typing import List, Optional, Tuple
import base64
import mimetypes
import os
import uuid


class GeminiMediaMixin:
    def _format_image_markdown(self, images) -> str:
        if not images:
            return ""

        def _extract_url(image_obj) -> str:
            if isinstance(image_obj, dict):
                image_url = image_obj.get("image_url") or image_obj.get("imageUrl") or {}
                if isinstance(image_url, dict):
                    return image_url.get("url", "") or image_url.get("uri", "")
                return image_url or image_obj.get("url", "")
            image_url = getattr(image_obj, "image_url", None) or getattr(image_obj, "imageUrl", None)
            if isinstance(image_url, dict):
                return image_url.get("url", "") or image_url.get("uri", "")
            if image_url:
                return image_url
            return getattr(image_obj, "url", "") or ""

        urls = [_extract_url(image) for image in images]
        return "\n\n".join([f"![image]({url})" for url in urls if url])

    def _save_generated_image(self, image_bytes: bytes, mime_type: Optional[str]) -> str:
        if not image_bytes:
            return ""
        ext = ".png"
        if mime_type:
            guessed_ext = mimetypes.guess_extension(mime_type)
            if guessed_ext:
                ext = guessed_ext
        filename = f"gemini_imagen_{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        return f"/uploads/{filename}"

    def _extract_inline_images(self, response) -> List[Tuple[bytes, Optional[str]]]:
        images: List[Tuple[bytes, Optional[str]]] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                inline = (
                    getattr(part, "inline_data", None)
                    or getattr(part, "inlineData", None)
                    or getattr(part, "file_data", None)
                    or getattr(part, "fileData", None)
                )
                if not inline:
                    continue
                data = getattr(inline, "data", None) or getattr(inline, "bytes", None)
                mime_type = getattr(inline, "mime_type", None) or getattr(inline, "mimeType", None)
                if isinstance(inline, dict):
                    data = inline.get("data") or inline.get("bytes")
                    mime_type = inline.get("mime_type") or inline.get("mimeType")
                if not data:
                    continue
                if isinstance(data, str):
                    try:
                        data_bytes = base64.b64decode(data)
                    except Exception:
                        continue
                else:
                    data_bytes = data
                if data_bytes:
                    images.append((data_bytes, mime_type))
        return images
