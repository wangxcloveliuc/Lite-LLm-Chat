from typing import List, Dict
from .base import BaseLLMProvider


class DoubaoProvider(BaseLLMProvider):
    id = "doubao"
    name = "Doubao"
    description = "Doubao (Volcengine Ark) language models"
    supported = True

    def __init__(self):
        from .doubao_client import doubao_client
        super().__init__(doubao_client)

    async def list_models(self) -> List[Dict[str, object]]:
        model_ids = [
            "doubao-1-5-vision-pro-32k-250115",
            "doubao-1-5-lite-32k-250115",
            "doubao-1-5-pro-32k-250115",
            "doubao-seed-1-6-vision-250815",
            "doubao-seed-1-6-flash-250828",
            "doubao-seed-1-6-lite-251015",
            "doubao-seed-1-6-251015",
            "doubao-seed-1-8-251228",
            "deepseek-r1-250528",
            "deepseek-v3-250324",
            "deepseek-v3-1-terminus",
            "deepseek-v3-2-251201",
            "kimi-k2-thinking-251104",
            "glm-4-7-251222",
            "doubao-seedream-4-5-251128",
            "doubao-seedream-4-0-250828",
            "doubao-seedance-1-5-pro-251215",
            "doubao-seedance-1-0-pro-250528",
            "doubao-seedance-1-0-pro-fast-251015",
            "doubao-seedance-1-0-lite-i2v-250428",
            "doubao-seedance-1-0-lite-t2v-250428",
        ]
        
        models = []
        for model_id in model_ids:
            # Generate name from id
            name = self._format_model_name(model_id)
            
            # Determine description based on model type
            if "seedream" in model_id.lower():
                desc_type = "image generation model"
            elif "vision" in model_id.lower():
                desc_type = "vision model"
            elif any(x in model_id.lower() for x in ["r1", "thinking", "seed"]):
                desc_type = "reasoning model"
            elif "code" in model_id.lower():
                desc_type = "code model"
            else:
                desc_type = "conversational model"
            
            models.append({
                "id": model_id,
                "name": name,
                "provider": self.id,
                "description": f"{name.split()[0]}'s {desc_type}",
            })
        
        return models


# Module-level provider instance expected by the registry
provider = DoubaoProvider()

