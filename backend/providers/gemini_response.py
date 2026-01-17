from typing import Dict, List, Tuple
import base64


class GeminiResponseMixin:
    def _extract_thought_signatures(self, response) -> List[str]:
        signatures: List[str] = []
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                sig = getattr(part, "thought_signature", None) or getattr(part, "thoughtSignature", None)
                if isinstance(part, dict):
                    sig = part.get("thought_signature") or part.get("thoughtSignature")
                if sig:
                    if isinstance(sig, (bytes, bytearray)):
                        sig = base64.b64encode(sig).decode("utf-8")
                    elif not isinstance(sig, str):
                        sig = str(sig)
                    signatures.append(sig)
        return signatures

    def _extract_search_results(self, response) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        candidates = getattr(response, "candidates", None) or []
        if isinstance(response, dict):
            candidates = response.get("candidates") or []

        for candidate in candidates:
            grounding = getattr(candidate, "grounding_metadata", None) or getattr(
                candidate, "groundingMetadata", None
            )
            if isinstance(candidate, dict):
                grounding = candidate.get("grounding_metadata") or candidate.get("groundingMetadata")
            if not grounding:
                continue
            chunks = getattr(grounding, "grounding_chunks", None) or getattr(
                grounding, "groundingChunks", None
            )
            if isinstance(grounding, dict):
                chunks = grounding.get("grounding_chunks") or grounding.get("groundingChunks")
            if not chunks:
                continue
            for chunk in chunks:
                web = getattr(chunk, "web", None)
                if isinstance(chunk, dict):
                    web = chunk.get("web") or chunk.get("web_data") or chunk.get("webData")
                url = None
                title = None
                content = None
                if web:
                    if isinstance(web, dict):
                        url = web.get("uri") or web.get("url") or web.get("link")
                        title = web.get("title") or web.get("name") or url
                    else:
                        url = getattr(web, "uri", None) or getattr(web, "url", None)
                        title = getattr(web, "title", None) or getattr(web, "name", None) or url
                if isinstance(chunk, dict):
                    url = url or chunk.get("uri") or chunk.get("url") or chunk.get("link")
                    title = title or chunk.get("title") or chunk.get("name")
                    content = chunk.get("content") or chunk.get("snippet")
                else:
                    url = url or getattr(chunk, "uri", None) or getattr(chunk, "url", None)
                    title = title or getattr(chunk, "title", None) or getattr(chunk, "name", None)
                    content = getattr(chunk, "content", None) or getattr(chunk, "snippet", None)
                if not url:
                    continue
                entry = {"url": url, "title": title or url}
                if content:
                    entry["content"] = content
                results.append(entry)

        deduped: List[Dict[str, str]] = []
        seen = set()
        for item in results:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(item)
        return deduped

    def _extract_url_context_results(self, response) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        candidates = getattr(response, "candidates", None) or []
        if isinstance(response, dict):
            candidates = response.get("candidates") or []

        response_metadata = getattr(response, "url_context_metadata", None) or getattr(
            response, "urlContextMetadata", None
        )
        if isinstance(response, dict):
            response_metadata = response.get("url_context_metadata") or response.get(
                "urlContextMetadata"
            )

        for candidate in candidates:
            metadata = getattr(candidate, "url_context_metadata", None) or getattr(
                candidate, "urlContextMetadata", None
            )
            if isinstance(candidate, dict):
                metadata = candidate.get("url_context_metadata") or candidate.get("urlContextMetadata")
            metadata = metadata or response_metadata
            if not metadata:
                continue
            url_metadata = getattr(metadata, "url_metadata", None) or getattr(
                metadata, "urlMetadata", None
            )
            if isinstance(metadata, dict):
                url_metadata = metadata.get("url_metadata") or metadata.get("urlMetadata")
            if not url_metadata:
                url_metadata = getattr(metadata, "retrieved_urls", None) or getattr(
                    metadata, "retrievedUrls", None
                )
            if isinstance(metadata, dict) and not url_metadata:
                url_metadata = metadata.get("retrieved_urls") or metadata.get("retrievedUrls")
            if isinstance(url_metadata, list):
                for item in url_metadata:
                    if isinstance(item, str):
                        results.append({"url": item, "title": item})
                        continue
                    if not isinstance(item, dict):
                        continue
                    url = item.get("retrieved_url") or item.get("url") or item.get("uri")
                    if not url:
                        continue
                    title = item.get("title") or url
                    status = item.get("url_retrieval_status") or item.get("status")
                    entry = {"url": url, "title": title}
                    if status:
                        entry["content"] = status
                    results.append(entry)

        deduped: List[Dict[str, str]] = []
        seen = set()
        for item in results:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(item)
        return deduped

    def _extract_text_and_reasoning(self, response) -> Tuple[str, str]:
        # Extract both thinking and regular text parts from the response in a single pass
        try:
            candidates = getattr(response, "candidates", None) or []
            if not candidates:
                return "", ""

            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []

            reasoning_parts: List[str] = []
            text_parts: List[str] = []

            for p in parts:
                text = getattr(p, "text", None)
                if not text:
                    continue

                has_thought = getattr(p, "thought", None)
                if has_thought is True:
                    # This is a thinking part
                    reasoning_parts.append(text)
                else:
                    # This is a regular text part (thought is None, False, or missing)
                    text_parts.append(text)

            reasoning = "\n".join([x for x in reasoning_parts if x])
            content_text = "".join([x for x in text_parts if x])
            return content_text, reasoning
        except Exception as e:
            print(f"Error extracting text and reasoning: {e}")
            return "", ""

    def _extract_reasoning_from_response(self, response) -> str:
        # Backward compatibility wrapper
        _, reasoning = self._extract_text_and_reasoning(response)
        return reasoning

    def _extract_regular_text_from_response(self, response) -> str:
        # Backward compatibility wrapper
        text, _ = self._extract_text_and_reasoning(response)
        return text
