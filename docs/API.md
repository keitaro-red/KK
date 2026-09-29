# KK API 契约

> **本文档回答**：前端要调某个功能，发什么请求、收什么响应、错了怎么办？
> **最后更新**: 2026-09-20（第 17 课 / 番外 17.7）
>
> **这是契约**——前端按它写代码。改动本文档 = 可能 break 前端。
> 实现细节（用了什么 ORM、内部函数名）不在这里，看代码。

---

## 一、通用约定

| 项 | 约定 |
|---|---|
| **统一前缀** | 所有业务接口在 `/api` 下（`main.py` 里 `include_router(router, prefix="/api")`） |
| Base URL（开发） | `http://localhost:5050`；前端通过 Vite 代理用相对路径 `/api/...` |
| 请求体格式 | JSON（**例外**：`/api/auth/token` 是 `application/x-www-form-urlencoded`） |
| 响应格式 | JSON |
| 交互式文档 | `/docs`（Swagger）、`/redoc`、`/openapi.json` 均开放 |

### 鉴权

| 项 | 约定 |
|---|---|
| 方式 | **JWT Bearer**，走 `Authorization` 请求头 |
| 格式 | `Authorization: Bearer <token>` —— **大小写敏感**，`Bearer` 后必须有一个空格 |
| 算法 / 有效期 | HS256 / **7 天** |
| JWT 载荷 | `sub`（**`str(user.id)`，注意不是 uid**）、`exp`、`iat`、`iss="kk-api"`。**不含 `role`** |
| 未登录时 | `401` + `{"detail": "请先登录"}`，响应头带 `WWW-Authenticate: Bearer` |
| 登出 / 吊销 | **无**（纯无状态 JWT，无 `jti`、无黑名单、无 refresh token） |

> ⚠️ JWT 里是 `user.id`（数据库自增 int 的字符串），但**业务属主校验用的是 `user.uid`**。每次请求后端会多查一次 `users` 表做转换。

### 统一错误格式

```json
{ "detail": "错误说明" }
```

常见状态码：

| 码 | 何时 | 说明 |
|---|---|---|
| `401` | 未登录 / token 无效或过期 | `detail` 固定为 `"请先登录"` |
| `404` | 资源不存在 **或不属于当前用户** | 两者**故意返回同一个 404**，不泄露他人资源的存在性 |
| `409` | 冲突（如用户名已存在） | |
| `422` | 请求体校验失败 | FastAPI 自动生成，格式是标准校验错误数组 |
| `500` | 未捕获异常 | 见"已知问题" |

### CORS

| 环境 | `allow_origins` |
|---|---|
| 设了环境变量 `KK_CORS_ORIGINS`（逗号分隔） | 按该值 |
| `KK_ENV` = `production` / `prod` | **空列表**（等于关闭跨域，必须显式配置） |
| 其它（开发默认） | `http://localhost:5173`、`http://127.0.0.1:5173` |

`allow_credentials=True`；允许的头包含 `Authorization`、`Content-Type`、`Last-Event-ID`。

> ⚠️ 生产环境若留空，跨域会**全部被拒**；且因为 `allow_credentials=True`，把 origins 配成 `*` 也不生效（CORS 规范禁止）。

---

## 二、端点总表

| # | 方法 | 路径 | 鉴权 | 职责 |
|---|---|---|---|---|
| 1 | GET | `/api/system/health` | 无 | 健康检查（含 DB 连通性） |
| 2 | POST | `/api/auth/register` | 无 | 注册并直接签发 JWT |
| 3 | POST | `/api/auth/token` | 无 | 登录换 JWT |
| 4 | GET | `/api/auth/me` | ✅ | 当前用户信息 |
| 5 | GET | `/api/chat/threads` | ✅ | 对话列表 |
| 6 | POST | `/api/chat/thread` | ✅ | 新建对话 |
| 7 | GET | `/api/chat/thread/{thread_id}/messages` | ✅ | 某对话的历史消息 |
| 8 | POST | `/api/chat/call` | ✅ | **非流式**调用 LLM（不落库） |
| 9 | POST | `/api/chat/stream` | ✅ | **流式**调用 LLM（SSE，落库） |
| 10 | POST | `/api/agent/runs` | ✅ | **创建 Agent run**（异步执行，立刻返回） |
| 11 | POST | `/api/agent/runs/{run_id}/cancel` | ✅ | 请求取消 run |
| 12 | GET | `/api/agent/runs/{run_id}` | ✅ | 查询 run 状态（**路径有 bug**，见第六节） |
| 13 | GET | `/api/agent/runs/{run_id}/events` | ✅ | **订阅 run 事件流**（SSE） |
| 14 | POST | `/api/agent/runs/{run_id}/resume` | ✅ | **从断点恢复** |

---

## 三、system

### 1. `GET /api/system/health`

健康检查，探测 PostgreSQL 连通性。

**响应**
```json
{ "status": "ok", "database": "connected" }
```

| 字段 | 取值 |
|---|---|
| `status` | `"ok"`（DB 通）/ `"degraded"`（DB 不通） |
| `database` | `"connected"` / `"disconnected"` |

**错误**：无（DB 探测失败被静默吞掉，返回 `degraded`）。

---

## 四、auth

### 2. `POST /api/auth/register`

注册新用户并**直接签发 JWT**（注册即登录）。

**请求体**（JSON）
```json
{ "username": "test", "password": "12345678" }
```

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `username` | string | 是 | 2–50 字符 |
| `password` | string | 是 | 8–128 字符，服务端 argon2id 哈希后入库 |

**响应** `201`
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "user_id": 1,
  "username": "test",
  "uid": "test_a3f9",
  "role": "user"
}
```

`uid` 是业务主键，格式 `<username>_<4位随机hex>`。

**错误**

| 码 | detail |
|---|---|
| `409` | `用户名已存在` |
| `422` | 长度不符（FastAPI 自动） |

### 3. `POST /api/auth/token`

登录换 JWT。

> ⚠️ **这是全项目唯一的表单接口**：`Content-Type: application/x-www-form-urlencoded`，**不是 JSON**。

**请求体**（表单）
```
username=test&password=password
```

**响应**：同 `/register` 的 `TokenResponse`。

**错误**

| 码 | detail | 备注 |
|---|---|---|
| `401` | `用户名或密码错误` | 用户不存在与密码错误**共用同一文案**（防用户名枚举，正确做法） |

### 4. `GET /api/auth/me`

**响应**
```json
{ "id": 1, "username": "test", "uid": "test_a3f9", "role": "user" }
```

**错误**：`401` `请先登录`

---

## 五、chat（旧链路：直连 LLM，不经 Agent）

> 📌 这一组是第 6-8 课建的"直连模型"链路，**不经过 Agent / 工具 / 中间件**。第 14 课之后的对话走 `agent/runs`。两组并存。

### 5. `GET /api/chat/threads`

当前用户全部对话，按 `updated_at` 倒序。

**响应**
```json
[
  { "thread_id": "uuid", "title": "新的对话", "created_at": "ISO8601", "updated_at": "ISO8601" }
]
```

### 6. `POST /api/chat/thread`

新建对话。**无请求体**。

**响应**：`{ "thread_id": "uuid", "title": "新的对话" }`

### 7. `GET /api/chat/thread/{thread_id}/messages`

某对话的历史消息，按 `created_at` 升序。

**响应**：`[{ "role": "user", "content": "..." }]`

**错误**

| 码 | detail | 备注 |
|---|---|---|
| `404` | `对话不存在` | 不存在**或不属于当前用户**都是这个（防探测） |

### 8. `POST /api/chat/call`

非流式调用 LLM，一次性返回完整回复。**不落库**。

**请求体**
| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `query` | string | 是 | 1–4000 字符 |
| `thread_id` | string \| null | 否 | **无校验，且本端点完全未使用** |

**响应**：`{ "response": "..." }`

**错误**：`401`；`422`；模型调用失败时 `500`（未捕获）。

### 9. `POST /api/chat/stream`

流式调用 LLM，SSE 逐 token 返回，**并持久化 user/assistant 两条消息**。

**请求体**：同 `/api/chat/call`。

**行为**：无 `thread_id` 时新建对话 → 先写 user 消息 → 流式产出 token → 结束后写 assistant 消息 → 发 `done`。

**响应**：SSE 流（事件见第七节）。

**错误**：`401`。模型异常发生在流开始之后，**无法再返回状态码**，连接直接断（没有 `done`）。

---

## 六、agent（Agent 链路）

### 10. `POST /api/agent/runs`

创建一次 Agent run：落库消息 + run 记录 → 投 ARQ 队列 → **立刻返回** `run_id`（不等结果）。

**请求体**
| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `query` | string | 是 | 1–4000 字符 |
| `thread_id` | string \| null | 否 | 缺省则服务端新建对话 |

**响应**
```json
{ "run_id": "uuid4", "thread_id": "uuid", "status": "pending" }
```

**错误**

| 码 | detail | 现状 |
|---|---|---|
| `401` | `请先登录` | |
| `422` | 长度校验 | |
| ~~`404`~~ | `对话线程不存在` | ⚠️ **实际返回 500**：服务层抛的 `ValueError` 没被 router 捕获 |

> ⚠️目前 `agent_slug` 被**服务端硬编码**为 `"ChatbotAgent"`，客户端无法选择 Agent。

### 11. `POST /api/agent/runs/{run_id}/cancel`

请求取消一个 run：DB 置 `cancel_requested` + 往 Redis 发取消信号（TTL 30 分钟）。

**无请求体。**

**响应**
```json
{ "run_id": "uuid", "status": "cancel_requested" }
```

**错误**：`404` `运行任务不存在`（不存在或非本人）。

> ⚠️ 若 run 已是终态，DB 不会改，但响应**仍**返回 `cancel_requested`——响应可能与真实状态不一致。

### 12. `GET /api/agent/runs/{run_id}` ⚠️ 路径有 bug


**响应**
```json
{ "run_id": "uuid", "status": "completed", "error_message": null }
```

`status` 取值见 `DATA_MODEL.md` 的状态机。

**错误**：`404`；`401`。

### 13. `GET /api/agent/runs/{run_id}/events` （SSE）

订阅 run 的事件流：轮询 Redis Stream 把 worker 产出的事件推给客户端。

**无请求体。**

**响应**：SSE 流（事件见第七节）。服务端**遇到 `end` 事件即主动关闭连接**。

**错误**：`401`。

> ⚠️ **不支持断线续传**：每次连接都从头（`after_seq = "0-0"`）开始，不读 `Last-Event-ID` 头。
> ⚠️ **无属主校验**：传别人的 `run_id` 能读到别人的内容；传不存在的 `run_id` 不会 404，而是**无限空转**（每 0.2s 查一次 Redis）。

### 14. `POST /api/agent/runs/{run_id}/resume` 

从断点恢复一个 `interrupted` 的 run。

**设计中的请求体**
```json
{ "decision": { "decisions": [{ "type": "approve" }] } }
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `decision` | object | 是 | 直接透传给 LangGraph 的 `Command(resume=...)`。**外层字段名是 `decision`，里层 `decisions` 是 LangChain 的格式**，别搞混 |

**响应**
```json
{ "run_id": "<新run_id>", "thread_id": "<原线程>", "status": "pending" }
```

**行为**：校验原 run 属于当前用户**且状态是 `interrupted`** → 新建一个 `run_type="resume"` 的 run（继承 `thread_id` 和 `agent_slug`）→ 入队。**原 run 保持 `interrupted` 不变**。

**错误**

| 码 | detail |
|---|---|
| `400` | `运行任务不存在` |
| `400` | `当前状态不可恢复：<status>` |
| `401` | `请先登录` |

> **模型不会被重新调用**。恢复是"接着走"不是"重新走"——`interrupt()` 停在 `after_model` hook 上，重放的是 hook，模型节点的产出已在 checkpointer 里。所以 resume **不额外消耗输入 token**，也不会产出与中断前**不同的**工具调用参数。
---

## 七、SSE 事件

事件格式由 `format_sse()` 统一生成：

```
event: <事件名>
data: <JSON>

```

（`\n\n` 结尾；**不写 `id:`，不写心跳注释**）

### 事件流 A：`/api/agent/runs/{run_id}/events`

事件由 **ARQ worker 进程**产生，写进 Redis Stream `run:event:{run_id}`（TTL 2 小时），SSE 端点轮询读出。

| `event` | payload | 含义 |
|---|---|---|
| `message` | `{"content": "..."}` | 一个增量 token |
| `end` | `{"status": "completed"}` | 正常结束 |
| `end` | `{"status": "cancelled"}` | 被取消 |
| `end` | `{"status": "interrupted"}` | 挂在审批断点，等待 resume |
| `end` | `{"status": "failed", "error": "..."}` | 失败 |
| `interrupt` | `{"interrupts": [ ... ]}` | **图挂在审批断点上**，payload 是 `HITLRequest`（含 `action_requests` 工具名与参数、`review_configs` 允许的决定）。前端据此弹审批窗 |

- `event` 字段缺省时回退为 `"message"`
- **`end` 是终止信号**，前端收到后应停止读取
- 事件类型无 `event:` 行时，`data` 是 JSON 字符串（由 `json.dumps(..., ensure_ascii=False)` 生成）

> ⚠️ **worker 被硬杀（SIGKILL）时既无 `end`、DB 也无终态**——客户端会永远挂着。前端需要超时兜底。

### 事件流 B：`/api/chat/stream`

事件由 **API 进程内联**产生（不经 Redis）。

| `event` | payload | 含义 |
|---|---|---|
| `message` | `{"content": "..."}` | 一个增量 token |
| `done` | `{"content": "", "thread_id": "uuid"}` | 正常结束（前端靠它拿到新建的 thread_id） |

> ⚠️ 与事件流 A **是两套**：终止事件名不同（`done` vs `end`），且此流**失败时不发任何终止事件**。

---

## 八、已知问题（bug 台账）

如实记录，不粉饰。修一个删掉一个。

### 🔴 阻断级


### 🟠 功能/安全

| # | 问题 | 位置 | 后果 |
|---|---|---|---|
| 7 | `create_agent_run_view` 的 `ValueError` 未捕获 | `server/routers/agent_router.py:47-53` | 非法 `thread_id` 返回 500 而非 404 |


### 🟡 隐患



### 修复建议顺序

```

```
