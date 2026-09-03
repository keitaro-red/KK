"""RUN 事件流：Redis Stream读写"""
import json

from kk.storage.redis.manager import get_redis

RUN_EVENT_TTL = 7200        # 事件流保留 2 小时

def _stream_key(run_id:str)->str:
    return f"run:event:{run_id}"

async def append_run_event(run_id:str,event_type:str,payload:dict)->str:
    """往 run 的事件流追加一条事件"""
    redis = await get_redis()
    key = _stream_key(run_id)
    event_id = await redis.xadd(
        key,
        {"event_type":event_type,"payload":json.dumps(payload)}
    )
    await redis.expire(key,RUN_EVENT_TTL)
    return event_id

async def list_run_events(run_id:str,after_seq:str="0-0",limit:int=200)->list[dict]:
    """读取run的事件流（从after_seq之后开始）"""
    redis = await get_redis()
    key = _stream_key(run_id)
    start = "-" if after_seq in {"0-0",""} else f"({after_seq}"
    rows = await redis.xrange(key,min=start,max="+",count=limit)

    events = []
    for event_id,fields in rows:
        events.append({
            "seq":event_id,
            "event_type":fields.get("event_type","message"),
            "payload":json.loads(fields.get("payload")or"{}")
        })
    return events
