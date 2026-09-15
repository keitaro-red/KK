"""RUN 事件流：Redis Stream读写"""
import json

from kk.storage.redis.manager import get_redis

# =========== run事件流部分 ============
# 添加，读取run事件

RUN_EVENT_TTL = 7200        # 事件流保留 2 小时


def _stream_key(run_id: str) -> str:
    """构建run事件字符串"""
    return f"run:event:{run_id}"


async def append_run_event(run_id: str, event_type: str, payload: dict) -> str:
    """往 run 的事件流追加一条事件"""
    redis = await get_redis()
    key = _stream_key(run_id)
    event_id = await redis.xadd(
        key,
        {"event_type": event_type, "payload": json.dumps(payload)}
    )
    await redis.expire(key, RUN_EVENT_TTL)
    return event_id


async def list_run_events(run_id: str, after_seq: str = "0-0", limit: int = 200) -> list[dict]:
    """读取run的事件流（从after_seq之后开始）"""
    redis = await get_redis()
    key = _stream_key(run_id)
    start = "-" if after_seq in {"0-0", ""} else f"({after_seq}"
    rows = await redis.xrange(key, min=start, max="+", count=limit)

    events = []
    for event_id, fields in rows:
        events.append({
            "seq": event_id,
            "event_type": fields.get("event_type", "message"),
            "payload": json.loads(fields.get("payload") or "{}")
        })
    return events

# ========= 取消请求部分 ==========
# 发布、清除和取消检查信号，根据run_id

CANCEL_KEY_TTL = 1800   # 取消信号30分钟


def _cancel_key(run_id: str) -> str:
    """构建run取消字符串"""
    return f"run:cancel:{run_id}"


async def publish_cancel_signal(run_id: str) -> None:
    """在Redis发布取消信号"""
    redis = await get_redis()
    await redis.set(_cancel_key(run_id), "1", ex=CANCEL_KEY_TTL)


async def has_cancel_signal(run_id: str) -> bool:
    """检查run_id的事件是否存在取消信号
    返回布尔值"""
    redis = await get_redis()
    return bool(await redis.get(_cancel_key(run_id)))


async def clear_cancel_signal(run_id: str) -> None:
    """清除取消信号"""
    redis = await get_redis()
    return redis.delete(_cancel_key(run_id))
