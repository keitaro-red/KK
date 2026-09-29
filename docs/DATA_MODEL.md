# KK 数据模型

> **本文档回答**：数据长什么样？表之间怎么关联？状态怎么流转？
> **最后更新**: 2026-09-22（版本 17.5）

---

## 一、总览

| 存储 | 用途 |
|---|---|
| **PostgreSQL 16** | 业务数据：用户、对话、消息、run 记录 + **LangGraph checkpointer**（图状态） |
| **Redis 7** | 事件流（Stream）+ 取消信号（String）+ **ARQ 任务队列** |

数据库里**只有 4 张业务表**。注意 `models/` 目录下有两个文件**不是表**：

| 文件 | 性质 |
|---|---|
| `models/providers.py` | 纯 dict `BUILTIN_PROVIDERS`（模型供应商配置），**无表** |
| `models/chat.py` | `LangChainChatAdapter` + `select_model()`，**无表** |

---

## 二、表结构

### 2.1 `users` —— 用户

| 列 | 类型 | 可空 | 默认 | 索引 | 说明 |
|---|---|---|---|---|---|
| `id` | Integer | 否 | 自增 | **PK** | 数据库自增。JWT 的 `sub` 存的就是它的字符串形式 |
| `username` | String(50) | 否 | — | — | ⚠️ **无 unique 约束**（只在应用层判重） |
| `uid` | String(64) | 否 | — | **unique + index** | **业务主键**，格式 `<username>_<4位hex>`。所有属主校验用它 |
| `password_hash` | String(255) | 否 | — | — | argon2id |
| `role` | String(20) | 否 | `"user"` | — | `user` / `admin`。**⚠️ 目前未被任何代码读取**（无角色鉴权） |
| `created_at` | DateTime | 是 | `utcnow` | — | naive UTC |

> **为什么有 `id` 和 `uid` 两个标识**：JWT 用 `id`（稳定、短），业务用 `uid`（可读、可跨系统）。代价是每次请求多一次 `users` 表查询做转换。

### 2.2 `conversations` —— 对话线程

| 列 | 类型 | 可空 | 默认 | 索引 | 说明 |
|---|---|---|---|---|---|
| `id` | Integer | 否 | 自增 | **PK** | |
| `thread_id` | String(64) | 否 | — | **unique + index** | UUID。**这是对外的线程标识**，也是 checkpointer 的索引键 |
| `uid` | String(64) | 否 | — | index | → `users.uid`（逻辑关联） |
| `agent_id` | String(64) | **是** | — | — | 预留（多 Agent 路由），目前恒为 NULL |
| `title` | String(255) | 是 | `"新的对话"` | — | |
| `created_at` | DateTime | 是 | `utcnow` | — | |
| `updated_at` | DateTime | 是 | `utcnow` + onupdate | — | 列表排序用它 |

ORM：`messages` relationship，`cascade="all, delete-orphan"`（删对话级联删消息）。

### 2.3 `messages` —— 消息

| 列 | 类型 | 可空 | 默认 | 索引 | 说明 |
|---|---|---|---|---|---|
| `id` | Integer | 否 | 自增 | **PK** | |
| `conversation_id` | Integer | 否 | — | index + **真 FK** | → `conversations.id` |
| `role` | String(20) | 否 | — | — | `user` / `assistant`（**无 DB 约束**） |
| `content` | Text | 否 | — | — | |
| `created_at` | DateTime | 是 | `utcnow` | — | |


### 2.4 `agent_runs` —— 一次 Agent 执行

| 列 | 类型 | 可空 | 默认 | 索引 | 说明 |
|---|---|---|---|---|---|
| `id` | String(64) | 否 | — | **PK** | `uuid4()`，由应用层生成 |
| `thread_id` | String(64) | 否 | — | index | → `conversations.thread_id`（逻辑关联，**注意指向 thread_id 不是 id**） |
| `uid` | String(64) | 否 | — | index | → `users.uid`（逻辑关联） |
| `agent_slug` | String(64) | 否 | — | — | Agent 标识（目前硬编码 `"ChatbotAgent"`） |
| `run_type` | String(20) | 否 | `"chat"` | — | `chat` / `resume`（**`resume` 尚无写入点**） |
| `input_message_id` | Integer | **是** | — | — | → `messages.id`（逻辑关联）。worker 靠它回查输入正文 |
| `status` | String(20) | 否 | `"pending"` | **无索引** | 见第四节状态机 |
| `error_type` | String(64) | 是 | — | — | 已定义但**未被写入** |
| `error_message` | Text | 是 | — | — | |
| `created_at` | DateTime | 是 | ⚠️ 见下 | — | |
| `started_at` | DateTime | 是 | — | — | `mark_running` 时写 |
| `finished_at` | DateTime | 是 | — | — | `mark_terminal` 时写 |
| `updated_at` | DateTime | 是 | ⚠️ 见下 | — | |
| `resume_decision` | Text | 是 | — | — | 存 resume 的决定，**JSON 字符串**（形如 `{"decisions":[{"type":"approve"}]}`）。只有 `run_type="resume"` 的行有值 |

### 2.5 checkpointer 表（LangGraph 建，非 KK 模型定义）

由 `kk/storage/postgres/checkpointer.py` 的 `saver.setup()` 创建，**不在 KK 的 `models/` 里**，因此 `create_all` 不管它们：

| 表 | 存什么 |
|---|---|
| `checkpoints` | 每个超级步的图状态快照（按 `thread_id` 索引）——**resume 就靠它** |
| `checkpoint_blobs` | 快照里的大字段（消息列表等）外置存储 |
| `checkpoint_writes` | 单步内的写入（中间态） |
| `checkpoint_migrations` | langgraph 自己的迁移版本号（它**自带**迁移管理，和 KK 无迁移框架形成对比） |

**建表时机**：**惰性**——`get_checkpointer()` 第一次被调用时（即第一次跑 Agent），不是进程启动时。所以「刚重启、还没跑过任务」时查不到这些表是正常的。


---

## 三、表之间的关系

**只有 1 条真外键约束**，其余都是逻辑关联（代码里 join，DB 无约束）：

| 关系 | 类型 |
|---|---|
| `messages.conversation_id` → `conversations.id` | ✅ **真 FK** |
| `Conversation.messages` ↔ `Message.conversation` | ORM relationship（级联删） |
| `agent_runs.thread_id` → `conversations.thread_id` | ❌ 逻辑关联 |
| `agent_runs.uid` → `users.uid` | ❌ 逻辑关联 |
| `agent_runs.input_message_id` → `messages.id` | ❌ 逻辑关联 |
| `conversations.uid` → `users.uid` | ❌ 逻辑关联 |
| `conversations.agent_id` → Agent 注册表 slug | ❌ 逻辑关联（非表） |

**所有权怎么实现**：不靠 FK，靠 repository 里显式 `WHERE` 过滤——`get_run_for_user(run_id, uid)`、`list_conversations(uid)`。

> ⚠️ 正因为没有 FK 也没有统一封装，**越权风险靠每个调用点自觉**——`/api/chat/stream` 就是漏了（见 `API.md` 第六节）。

---

## 四、状态机

### 4.1 `AgentRun.status`

**终态集合**（`models/agent_run.py`）：

```python
TERMINAL_RUN_STATUSES = {"completed", "failed", "cancelled", "interrupted"}
```

| 取值 | 含义 | 谁写的 |
|---|---|---|
| `pending` | 已入库，等待 worker 取 | 默认值 / `create_run` |
| `running` | worker 正在执行 | `mark_running`（同时写 `started_at`） |
| `cancel_requested` | **中间态**：API 已请求取消 | `request_cancel` |
| `completed` | ✅ 终态，正常跑完 | worker |
| `failed` | ✅ 终态，出错 | worker（含"输入消息不存在"） |
| `cancelled` | ✅ 终态，被取消 | worker |
| `interrupted` | ✅ 终态，图挂起等审批 | worker在**流结束后回查图状态**（`get_pending_interrupt`）写入 |

> ⚠️ 模型里 `status` 列的 comment 写的是 `pending/running/completed/failed`——**已过期**，漏了后三个。

### 4.2 迁移图

```
                     create_run()
                         │
                         ▼
                    ┌─────────┐
                    │ pending │
                    └────┬────┘
      request_cancel()   │   mark_running()
            ┌────────────┘   └────────────┐
            ▼                             ▼
   ┌──────────────────┐            ┌─────────┐
   │ cancel_requested │◀───────────│ running │
   └────────┬─────────┘ request_cancel()
            │                          │
            │                          ├──▶ completed   ✅
            └── worker 检测到          ├──▶ failed      ✅
                run:cancel 信号        └──▶ cancelled   ✅
```

### 4.3 三条规则（都实现在 repository 里，守卫相同）

| 迁移 | 方法 | 副作用 |
|---|---|---|
| 任意非终态 → `running` | `mark_running` | 写 `started_at` |
| 任意非终态 → `cancel_requested` | `request_cancel` | 无时间戳（Redis 信号由服务层发） |
| 任意非终态 → 指定终态 | `mark_terminal(status, error_message)` | 写 `finished_at`、`error_message` |
| **终态 → 任何状态** | ❌ **被拒绝** | 守卫 `if run.status not in TERMINAL_RUN_STATUSES` |

**三条方法共用的守卫是这套状态机的核心**：

> 终态**不可覆盖**。一旦 `completed`/`failed`/`cancelled`/`interrupted`，后续任何写状态的尝试都被静默忽略。

**关键语义**：`cancel_requested` **不属于终态**——所以 `mark_terminal("completed")` 能覆盖它。"取消请求发出后 Agent 恰好跑完"是合法路径（任务确实做完了）。

> ⚠️ 反过来，如果把 `cancel_requested` 错放进终态集合，这条路径会被永久拒绝，run 会卡在"取消请求中"。

### 4.4 已知缺口

1. **`cancel_requested` → `running` 可达**：`process_agent_run` 只挡终态，拿到 `cancel_requested` 的 run 会照常 `mark_running`，中间态被覆盖。最终靠 Redis 里残留的 `run:cancel:` 信号纠正为 `cancelled`。
3. **`mark_terminal` 在 worker 的 `failed` 分支缺 `commit`**，靠 session 上下文退出时兜底。

### 4.5 `AgentRun.run_type`

| 取值 | 含义 | 现状 |
|---|---|---|
| `chat` | 普通对话（默认） | 唯一被实际写入的值 |
| `resume` | 从 `interrupted` 恢复 | **仅存在于列注释和讲义** |

### 4.6 其他受约束取值

| 枚举 | 取值 | 位置 |
|---|---|---|
| `Message.role` | `user` / `assistant` | 无 DB 约束 |
| `User.role` | `user` / `admin` | 无 DB 约束，**未被使用** |
| `tool_approval_mode` | `default` / `always_trust` | 非法值抛 `ValueError` |
| 审批决定 | `approve` / `reject` | 见讲义番外 17.5 |
| 受审批工具 | `write_file` / `edit_file` / `execute` | `agents/tool_approval.py` |

---

## 五、Redis 键空间

### 5.1 KK 自己写的 key（集中在 `services/run_queue_service.py`）

| key | 结构 | TTL | 用途 |
|---|---|---|---|
| `run:event:{run_id}` | **Stream** | **7200s（2h）**，每次 `XADD` 后重新 `EXPIRE` 续期 | run 的 token 事件流；SSE 端点 `XRANGE` 轮询 |
| `run:cancel:{run_id}` | **String**（值 `"1"`） | **1800s（30min）** | 取消信号：API `SET`、worker 每 0.2s `GET` 轮询、`finally` 里 `DEL` |

- Stream 字段：`event_type` + `payload`（payload 是 `json.dumps` 后的**字符串**，读出再 `json.loads`）
- 客户端 `decode_responses=True`，所以 key 能直接当字符串比较

> ⚠️ **key 是单数 `run:event:`**（部分讲义里写成复数 `run:events:`，以代码为准）。
> ⚠️ 若事件流长时间无新事件，2 小时后 key 整体消失——仍在轮询的 SSE 会读到空。

### 5.2 ARQ 框架自己的 key（KK 代码里不出现）

| key | 结构 | 用途 |
|---|---|---|
| `arq:queue` | ZSET | **任务队列**，`enqueue_job` 落这里 |
| `arq:job:{job_id}` | String | job 定义 |
| `arq:result:{job_id}` | String | job 结果（`keep_result` 默认 3600s） |
| `arq:in-progress:{job_id}` | String | 防重复执行 |
| `arq:retry:{job_id}` | String | 重试计数 |

KK 未覆盖任何 ARQ 默认值，所以 `job_timeout=300s`、`max_tries=5`、`poll_delay=0.5s` 都是默认。

### 5.3 连接

- `redis://redis:6379/0`（db=0），`aioredis.from_url(..., decode_responses=True)`
- **ARQ 连接池每进程一份**：API 进程的 `_pool` 和 worker 进程的 `_pool` 各自独立，不共享

---

## 六、建表机制（重要）

### 6.1 三条并行的建表路径

| # | 机制 | 入口 | 范围 | 支持迁移？ |
|---|---|---|---|---|
| ① | SQLAlchemy `create_all` | `PostgresManager.create_tables()` | KK 的 4 张业务表 | ❌ **完全不支持 ALTER** |
| ② | LangGraph `AsyncPostgresSaver.setup()` | `storage/postgres/checkpointer.py`（惰性，首次调用执行） | checkpointer 元数据表（`checkpoints` / `checkpoint_blobs` / `checkpoint_writes` 等） | ✅ 自带 `checkpoint_migrations` 版本管理 |
| ③ | **手工 DDL** | `psql` 命令 | 改列/删列时的唯一手段 | — |

**调用点**（都只在启动时跑一次）：
- API 进程：`server/utils/lifespan.py`（`initialize()` + `create_tables()`）
- Worker 进程：`services/run_worker.py` 的 `_worker_startup`

### 6.2 🔴 `create_all` 的语义 = `CREATE TABLE IF NOT EXISTS`

> **表不存在才建，已存在直接跳过，永不 ALTER。**

这意味着：**改了模型里的列，旧库不会自动更新**。必须手工处理：

```bash
# 方式 A：删表重建（数据会没）
docker exec -it kk-postgres psql -U <user> -d <db> -c "DROP TABLE agent_runs;"
# 然后重启 api/worker，create_tables() 按新模型重建

# 方式 B：手工加列（保留数据）
docker exec -it kk-postgres psql -U <user> -d <db> -c \
  "ALTER TABLE agent_runs ADD COLUMN resume_decision TEXT;"
```

### 6.3 历次改表记录

| 版本 | 变更 | 手工方案 |
|---|---|---|
| 08 | `conversations.agent_id` 从 NOT NULL 改可空 | `ALTER TABLE ... DROP NOT NULL;` 或删表重建 |
| 15 | `agent_runs` 删 `query` 列，加 `input_message_id` / `run_type` / `error_type` / `started_at` / `finished_at` | DROP 重建，或逐列 ALTER |
| 17.5 | `agent_runs` 加 `resume_decision TEXT` | **待执行** |
| 17.5 | `agent_runs` 加 `resume_decision TEXT` | `ALTER TABLE agent_runs ADD COLUMN resume_decision TEXT;`（或删表重建） |

> 📌 **KK 没有迁移框架**（无 Alembic）。生产级项目应上迁移工具，记在 `DECISIONS.md`。

### 6.4 ⚠️ 隐式 import 依赖（脆弱点）

`create_tables()` 只显式 import 了两个模型：

```python
from kk.models.user import Base
from kk.models import conversation
```

`agent_runs` 表能建出来，**完全靠 import 副作用链**：`agent_router` → `agent_run_repository` → `models.agent_run` 把 `AgentRun` 提前注册进 `Base.metadata`。

**这是侥幸**——`models/__init__.py` 是空的。修法：把 `agent_run` 加进 `create_tables` 的 import，或在 `models/__init__.py` 里统一 import 所有模型。

---

## 七、不在数据库里的"状态"

这些是**容易误认成表**的东西：

| 东西 | 实际存在哪 |
|---|---|
| LangGraph 图状态（消息历史、中断断点） | **checkpointer 表**（Postgres，由 `AsyncPostgresSaver` 管理） |
| `BaseState.artifacts` | 图的 state（进 checkpointer），**不是表** |
| `BaseContext`（`thread_id`/`uid`/`model`/`summary_threshold`/`tool_approval_mode`…） | 运行时配置对象，**不是表** |
| 附件（`AttachmentMiddleware` 读的 `state["uploads"]`） | 图的 state，**目前无附件表、无持久化** |
| run 的实时 token | Redis Stream，**TTL 2 小时后消失** |
