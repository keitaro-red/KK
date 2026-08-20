"""LLM 调用"""
from langchain_openai import ChatOpenAI

from kk.config import config
from kk.models.providers import BUILTIN_PROVIDERS


class LangChainChatAdapter:
    """封装 LangChain，统一对外call接口"""

    def __init__(self, model, model_name: str, base_url: str):
        self.model = model
        self.model_name = model_name
        self.base_url = base_url

    async def call(self, message: str) -> str:
        """非流式调用"""
        message = [{"role": "user", "content": message}]
        try:
            response = await self.model.ainvoke(message)
            return response.content
        except Exception as e:
            raise Exception(
                f"模型调用失败：{e}，URL：{self.base_url}，Model：{self.model_name}")

    async def stream(self, message: str):
        """流式调用"""
        messages = [{"role": "user", "content": message}]
        async for chunk in self.model.astream(messages):
            if chunk.content:
                yield chunk.content


def select_model(model_spec: str) -> LangChainChatAdapter:
    """根据model spec（provider_id:model_id）构造可调用的模型"""
    if not model_spec:
        raise ValueError("model_spec 不能为空")

    provider_id, model_id = model_spec.split(":", 1)

    provider = next(
        (p for p in BUILTIN_PROVIDERS if p["provider_id"] == provider_id),
        None
    )
    if provider is None:
        raise ValueError(f"未知的供应商:'{provider_id}'")

    api_key = getattr(config, provider["api_key_env"], "")
    if not api_key:
        raise ValueError(f"确实API key:'{provider['api_key_env']}'")

    model = ChatOpenAI(
        model=model_id,
        api_key=api_key,
        base_url=provider["base_url"],
    )
    return LangChainChatAdapter(model, model_name=model_id, base_url=provider["base_url"])
