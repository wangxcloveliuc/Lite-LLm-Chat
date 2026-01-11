from typing import List, Dict
from .base import BaseLLMProvider


class SiliconFlowProvider(BaseLLMProvider):
    id = "siliconflow"
    name = "SiliconFlow"
    description = "SiliconFlow (OpenAI-compatible) language models"
    supported = True

    def __init__(self):
        from .siliconflow_client import siliconflow_client
        super().__init__(siliconflow_client)

    async def list_models(self) -> List[Dict[str, object]]:

        # Keeping this small and safe; you can extend via env/config if needed.
        model_ids = [
            "THUDM/GLM-Z1-Rumination-32B-0414",
            "Pro/THUDM/glm-4-9b-chat",
            "Pro/Qwen/Qwen2-7B-Instruct",
            "Pro/Qwen/Qwen2.5-7B-Instruct",
            "Pro/Qwen/Qwen2.5-Coder-7B-Instruct",
            "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "THUDM/glm-4-9b-chat",
            "Qwen/Qwen2-7B-Instruct",
            "internlm/internlm2_5-7b-chat",
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/deepseek-vl2",
            "Qwen/Qwen2.5-72B-Instruct-128K",
            "Qwen/Qwen2-VL-72B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "deepseek-ai/DeepSeek-V2.5",
            "Qwen/QVQ-72B-Preview",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
            "Qwen/Qwen2.5-VL-72B-Instruct",
            "Qwen/QwQ-32B",
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "THUDM/GLM-4-9B-0414",
            "THUDM/GLM-Z1-9B-0414",
            "THUDM/GLM-4-32B-0414",
            "THUDM/GLM-Z1-32B-0414",
            "ascend-tribe/pangu-pro-moe",
            "Qwen/Qwen3-8B",
            "Qwen/Qwen3-14B",
            "Qwen/Qwen3-32B",
            "Qwen/Qwen3-30B-A3B",
            "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "Tongyi-Zhiwen/QwenLong-L1-32B",
            "MiniMaxAI/MiniMax-M1-80k",
            "moonshotai/Kimi-Dev-72B",
            "tencent/Hunyuan-A13B-Instruct",
            "baidu/ERNIE-4.5-300B-A47B",
            "Pro/THUDM/GLM-4.1V-9B-Thinking",
            "THUDM/GLM-4.1V-9B-Thinking",
            "Qwen/Qwen3-235B-A22B-Instruct-2507",
            "Qwen/Qwen3-235B-A22B-Thinking-2507",
            "Qwen/Qwen3-30B-A3B-Instruct-2507",
            "Qwen/Qwen3-30B-A3B-Thinking-2507",
            "Qwen/Qwen3-Coder-480B-A35B-Instruct",
            "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "stepfun-ai/step3",
            "zai-org/GLM-4.5-Air",
            "zai-org/GLM-4.5V",
            "ByteDance-Seed/Seed-OSS-36B-Instruct",
            "tencent/Hunyuan-MT-7B",
            "inclusionAI/Ling-mini-2.0",
            "inclusionAI/Ling-flash-2.0",
            "inclusionAI/Ring-flash-2.0",
            "Qwen/Qwen3-Next-80B-A3B-Thinking",
            "Qwen/Qwen3-Next-80B-A3B-Instruct",
            "Pro/moonshotai/Kimi-K2-Instruct-0905",
            "moonshotai/Kimi-K2-Instruct-0905",
            "deepseek-ai/DeepSeek-OCR",
            "Qwen/Qwen3-Omni-30B-A3B-Captioner",
            "Qwen/Qwen3-Omni-30B-A3B-Thinking",
            "Qwen/Qwen3-Omni-30B-A3B-Instruct",
            "Qwen/Qwen3-VL-235B-A22B-Thinking",
            "Qwen/Qwen3-VL-235B-A22B-Instruct",
            "Qwen/Qwen3-VL-30B-A3B-Thinking",
            "Qwen/Qwen3-VL-30B-A3B-Instruct",
            "Qwen/Qwen3-VL-8B-Thinking",
            "Qwen/Qwen3-VL-8B-Instruct",
            "Qwen/Qwen3-VL-32B-Thinking",
            "Qwen/Qwen3-VL-32B-Instruct",
            "Kwaipilot/KAT-Dev",
            "zai-org/GLM-4.6",
            "MiniMaxAI/MiniMax-M2",
            "Pro/moonshotai/Kimi-K2-Thinking",
            "moonshotai/Kimi-K2-Thinking",
            "zai-org/GLM-4.6V",
            "Pro/deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-V3",
            "Pro/deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-R1",
            "Pro/deepseek-ai/DeepSeek-V3.1-Terminus",
            "deepseek-ai/DeepSeek-V3.1-Terminus",
            "Pro/deepseek-ai/DeepSeek-V3.2",
            "deepseek-ai/DeepSeek-V3.2",
            "Pro/zai-org/GLM-4.7",
        ]

        models: List[Dict[str, object]] = []
        for model_id in model_ids:
            name = self._format_model_name(model_id)
            models.append(
                {
                    "id": model_id,
                    "name": name,
                    "provider": self.id,
                    "description": f"{name}",
                }
            )
        return models



# Module-level provider instance expected by the registry
provider = SiliconFlowProvider()
