"""图片兼容降级中间件"""
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ModelResponse
from langchain_core.messages import AIMessage

def _has_image(messages)->bool:
    """判断消息里是否有图片"""
    for message in messages:
        for block in getattr(message,"content_blocks",[]):
            if isinstance(block,dict) and block.get("type") in {"image","image_url","input_image"}:
                return True
    return False

def _is_image_rejection(exc:Exception)->bool:
    """判断错误是不是模型不支持图片"""
    detail = str(exc).lower()
    return "image" in detail and any(
        term in detail for term in ("not support", "unsupported", "not allowed", "not a vlm")
    )


# def _ocr_fallback_response(paths):
#     """生成OCR工具调用，用ocr试图"""
    
class ImageInputCompatibilityMiddleware(AgentMiddleware):
    """模型不支持图片时，降级为OCR提示"""
    async def awrap_model_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as exc:
            if _has_image(request.messages) and _is_image_rejection(exc):
                return ModelResponse(result=[AIMessage(content="当前模型不支持图片输入，请改用OCR工具提前图片文字")])
            raise
    