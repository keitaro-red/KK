"""文件系统工具：读/写/改/列/搜/执行，全部限制在工作目录内"""

import subprocess
from pathlib import Path

from kk.agents.toolkits.filesystem.path import resolve_workspace_path,WORKSPACE_ROOT
from kk.agents.toolkits.registry import tool

# 截断文件防止token爆炸
MAX_HEAD_CHARS = 4000


@tool(category="filesystem", tags=["文件"], display_name="读文件")
def read_file(path: str) -> str:
    """读取工作目录内的文本文件内容"""
    try:
        p = resolve_workspace_path(path)
        content = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: 文件不存在{path}"
    except ValueError as e:
        return f"Error: {e}"

    if len(content) > MAX_HEAD_CHARS:
        return content[:MAX_HEAD_CHARS]+"\n...[内容过长已截断，请用grep定位后分段读取]"
    return content


@tool(category="filesystem", tags=["文件"], display_name="写文件")
def write_file(path: str, content: str) -> str:
    """把内容写入工作目录内的文件（覆盖已有文件）"""
    try:
        p = resolve_workspace_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    except ValueError as e:
        return f"Error: {e}"
    return f"已写入{path}"


@tool(category="filesystem", tags=["文件"], display_name="编辑文件")
def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    """在工作目录内的文件中，把old_string替换为new_string"""
    try:
        p = resolve_workspace_path(path)
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: 文件不存在{path}"
    except ValueError as e:
        return f"Error: {e}"

    count = text.count(old_string)
    if count == 0:
        return f"Error: 未找到要替换的字符串:{old_string}"
    if count > 1 and not replace_all:
        return f"Error: 该字符串出现 {count} 次，请用 replace_all=True 或提供更精确的上下文"

    new_text = text.replace(old_string, new_string) if replace_all else text.replace(
        old_string, new_string, 1)
    p.write_text(new_text, encoding="utf-8")
    return f"已编辑 {path}，替换 {count if replace_all else 1} 处"

@tool(category="filesystem", tags=["文件"], display_name="列目录")
def ls(path: str = ".") -> str:
    """列出工作目录内某个目录的内容。"""
    try:
        p = resolve_workspace_path(path)
        entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except FileNotFoundError:
        return f"Error: 目录不存在: {path}"
    except ValueError as e:
        return f"Error: {e}"

    lines = []
    for e in entries:
        marker = "/" if e.is_dir() else ""
        lines.append(f"{e.name}{marker}")
    return "\n".join(lines) if lines else "(空目录)"

@tool(category="filesystem", tags=["文件"], display_name="搜索内容")
def grep(pattern: str, path: str = ".") -> str:
    """在工作目录的文件搜索文本，返回匹配行"""
    try:
        base = resolve_workspace_path(path)
    except ValueError as e:
        return "Error: {e}"

    if not base.exists():
        return "Error: 路径不存在:{path}"

    files = base.rglob("*") if base.is_dir() else [base]
    matchs = []
    for f in files:
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern in line:
                rel = f.relative_to(base)
                matchs.append(f"{rel}:{i}:{line}")
    return "\n".join(matchs[:200])if matchs else "未找到匹配"

@tool(category="filesystem", tags=["文件"], display_name="搜索文件")
def glob(pattern:str,path:str=".")->str:
    """按通配符模式搜索工作目录内的文件"""
    try:
        base = resolve_workspace_path(path)
    except ValueError as e:
        return f"Error: {e}"

    matchs = sorted(str(f.relative_to(base))for f in base.rglob(pattern))
    return "\n".join(matchs[:200])if matchs else "未找到匹配"

@tool(category="filesystem", tags=["文件", "执行"], display_name="执行命令")
def execute(command:str)->str:
    """在工作目录内执行shell命令，返回stdout/stderr 和退出码"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutError:
        return "Error: 命令执行超时（30秒）"

    output = result.stdout or ""
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    if result.returncode != 0:
        output += f"\n[退出码{result.returncode}]"
    return output or "(无输出)"