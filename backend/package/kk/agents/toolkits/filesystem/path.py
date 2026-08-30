"""文件工具的路径距离"""
from pathlib import Path

from kk.config import config

# 工具目录根
WORKSPACE_ROOT = Path(config.WORKSPACE_DIR).resolve()

def resolve_workspace_path(path:str)->Path:
    """
    把相对路径解析到WORKSPACE_ROOT内，拒绝路径穿越
    - 拒绝绝对路径
    - 拒绝包含“..”的路径
    - resolve 后二次确认在WORKSPACE_ROOT内
    """
    raw = str(path or "").strip()
    if not raw:
        raise ValueError("path 不能为空")

    p = Path(raw)
    if p.is_absolute():
        raise ValueError("只允许相对路径")
    if ".." in p.parts:
        raise ValueError("路径不能包含 ‘..’")

    full = (WORKSPACE_ROOT / p).resolve()
    if not full.is_relative_to(WORKSPACE_ROOT):
        raise ValueError("路径逃逸出工作目录")
    return full