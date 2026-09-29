"""附件注入"""

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage

def _build_attachment_prompt(uploads)->str|None:
    """把文件列表渲染成提示词"""
    valid =[]
    for upload in uploads:
        path = upload.get("path")
        name = upload.get("file_name","未知文件")
        if isinstance(path,str) and path.strip():
            valid.append((name,path))

    if not valid:
        return None

    lines = ["用户上传了以下文件：",""]
    for name,path in valid:
        lines.append(f"- {name}: {path}")
    lines.append("请优先使用read_file工具读取这些文件内容，再回答用户问题")
    return "\n".join(lines)


class AttachmentMiddleware(AgentMiddleware):
    """从 state.upload 读取文件，注入system_prompt"""

    async def awrap_model_call(self, request, handler):
        uploads = request.state.get("uploads",[])
        if uploads:
            prompt = _build_attachment_prompt(uploads)
            if prompt:
                existing = request.system_message.content if request.system_message else ""
                merged = f"{existing}\n\n{prompt}" if existing else prompt
                request = request.override(system_message=SystemMessage(content=merged))
        return await handler(request)
