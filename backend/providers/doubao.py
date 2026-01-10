from typing import List, Dict, Optional, Tuple

class DoubaoProvider:
    id = "doubao"
    name = "Doubao"
    description = "Doubao (Volcengine Ark) language models"
    supported = True

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        from .doubao_client import doubao_client
        return await doubao_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        max_tokens: Optional[int] = None,
    ):
        from .doubao_client import doubao_client
        async for chunk in doubao_client.stream_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    async def list_models(self) -> List[Dict[str, object]]:
        model_ids = [
            "doubao-1-5-lite-32k-250115",
            "doubao-1-5-pro-32k-250115",
            "doubao-1-5-vision-pro-32k-250115",
            "deepseek-r1-250528",
            "deepseek-v3-250324",
            "doubao-seed-1-6-flash-250828",
            "doubao-seed-1-6-251015",
            "kimi-k2-thinking-251104",
            "doubao-seed-1-6-vision-250815",
            "deepseek-v3-1-terminus",
            "doubao-seed-code-preview-251028",
            "doubao-seed-1-6-lite-251015",
            "deepseek-v3-2-251201",
            "doubao-seed-1-8-251228",
        ]
        
        models = []
        for model_id in model_ids:
            # Generate name from id
            name_parts = model_id.replace("-", " ").title().split()
            name = " ".join(name_parts)
            
            # Determine description based on model type
            if "vision" in model_id.lower():
                desc_type = "vision model"
            elif any(x in model_id.lower() for x in ["r1", "thinking", "seed"]):
                desc_type = "reasoning model"
            elif "code" in model_id.lower():
                desc_type = "code model"
            else:
                desc_type = "conversational model"
            
            # Extract context length from id if present
            context = ""
            
            models.append({
                "id": model_id,
                "name": name,
                "provider": "doubao",
                "description": f"{name.split()[0]}'s {desc_type}{context}",
            })
        
        return models

# Module-level provider instance expected by the registry
provider = DoubaoProvider()
