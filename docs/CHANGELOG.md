# 变更日志

> **本文档回答**：某个版本加了什么？
> **面向**：使用者/协作者。写"做了什么能力"，**不写**设计理由（→ `DECISIONS.md`）。
>
> **最后更新**: 2026-09-22

---
## [17.6a] — 2026-09-28　样式基线 + Element Plus + 组件化

### 新增
- **引入 Element Plus**（全量引入 + 中文语言包）
- **样式基线**：`styles/reset.css`（全局 reset）+ `styles/theme.css`（设计变量 + 主题覆盖）
- **聊天页组件化**：拆成 `ChatSidebar` / `ConversationList` / `ChatHeader` / `MessageList` / `MessageBubble` / `ChatComposer`
- **组合式函数**：`useChatMessages`（消息数据结构）、`useRunStream`（SSE 消费，零状态）
- **侧边栏可收起**
- 消息条目改用稳定 `id` 作 key（原用数组下标）

### 变更
- **输入框改为 Enter 发送、Shift + Enter 换行**（通用习惯；配 `isComposing` 守卫挡住中文输入法的选词回车）
- 登录页改用 `el-card` / `el-form` / `el-input` / `el-button`
- 全站颜色收成 CSS 变量（原散落硬编码）

### 移除
- `components/ApprovalDialog.vue`（孤儿半成品，17.6c 由 `ApprovalCard.vue` 取代）

### 修复
- 会话列表的选中高亮（`.active` 原来有 class 无样式）
- 消除裸标签选择器（`.chat-input button` 等）——它们会穿透进 Element Plus 组件内部
- `ChatView` 的全局 `*` 重置搬出页面文件


---
## [版本 17.5] — 2026-09-22　持久化 checkpointer + resume

### 新增
- **持久化 checkpointer**：图状态从进程内存改存 Postgres（`AsyncPostgresSaver`），跨进程、跨重启不丢
- **工具审批从"能暂停"变成"能暂停也能继续"**：`POST /api/agent/runs/{id}/resume`
- **`interrupted` 状态正式落地**：worker 在流结束后回查图状态，中断不再被误标为 `completed`
- SSE 新增 `interrupt` 事件，前端可据此弹出审批框

### 变更
- `agent_runs` 表新增 `resume_decision` 列
- `BaseAgent` 的流式方法支持传入任意图输入（普通消息 or `Command(resume=...)`）
- **模型回复现在会落库**：此前 agent 链路只存 user 消息，回复仅存在于 Redis Stream（2h 后消失），刷新页面就丢历史

## [17] — 2026-09-20　附件与工具审批

### 新增
- **工具审批**：`write_file` / `edit_file` / `execute` 三个敏感工具执行前需用户 approve/reject
- **附件注入中间件**：把上传文件列表拼进 system_prompt，引导 Agent 用 `read_file` 按需读取
- **图片兼容降级中间件**（骨架）：模型不支持图片时返回提示，引导改用 OCR
- **前端审批弹窗组件** `ApprovalDialog.vue`（**未接线**，待 resume 打通）

### 变更
- 中间件构建从 `get_graph` 内联抽成 `_build_middleware(context)`

### 已知问题
- 审批中断后 run 被误标为 `completed`（`interrupted` 状态无写入点），修复在番外 17.5
- `ChatbotAgent.get_graph` 仍引用已删除的 `self.checkpointer` → run 必失败

---

## [16] — 2026-09-17　中间件栈（上）：上下文压缩与重试

### 新增
- **中间件栈骨架**：`create_agent(middleware=[...])`
- **Token 用量统计中间件**：统计并回写 `token_usage` state
- **上下文压缩中间件（L1）**：超阈值时截断过长的工具结果
- **模型重试中间件**：模型调用失败自动重试

### 变更
- Agent 首次拥有可插拔的中间件链

---

## [15] — 2026-09-13　Run 生命周期管理

### 新增
- **Run 状态机**：`pending` / `running` / `cancel_requested` / `completed` / `failed` / `cancelled` / `interrupted`
- **取消 run**：`POST /api/agent/runs/{id}/cancel`，Redis 信号 + worker 竞速取消
- **查询 run 状态**：`GET /api/agent/runs/{id}`
- **前端聊天页支持取消**

### 变更
- `agent_runs` 表重构：删 `query` 列，改为 `input_message_id` 关联到 `messages` 表；新增 `run_type` / `error_type` / `started_at` / `finished_at`
- 终态不可覆盖（`TERMINAL_RUN_STATUSES` 守卫）

### 已知问题
- `GET /api/agent/runs/{id}` 实际路径注册成了 `/api/agentruns/{id}`（缺斜杠）

---

## [14] — 2026-09-10　ARQ Worker：离线执行 Agent

### 新增
- **ARQ 任务队列**：Agent 执行从 HTTP 请求中剥离，改为异步任务
- **Redis Stream 事件流**：`run:event:{run_id}`，SSE 端点轮询消费
- **服务层** `kk/services/`：业务编排从 router 中抽出（跨进程共享）
- **`agent_runs` 表**：记录每次执行
- `POST /api/agent/runs` + `GET /api/agent/runs/{id}/events`（SSE）
- 前端切换到"创建 run → 订阅事件流"两步式

### 变更
- 容器从 3 个增加到 5 个（新增 `worker`）

---

## [13] — 2026-09-06　工具系统（下）：Filesystem 工具

### 新增
- **文件工具**：`read_file` / `write_file` / `edit_file` / `ls` / `grep` / `glob` / `execute`
- **路径隔离**：`paths.py`，所有文件操作限制在 `WORKSPACE_DIR` 内

---

## [12] — 2026-09-03　工具系统（上）：@tool 装饰器与注册

### 新增
- **工具注册表**：`@tool` 装饰器 + 元数据注册
- **工具服务** `resolve_runtime_tools(context)`：按 context 过滤可用工具
- 内置工具：`calculator`、`get_current_time`
- Agent 首次具备 Function Calling 能力

---

## [11] — 2026-08-30　ChatbotAgent + Agent 路由

### 新增
- **`ChatbotAgent`**：第一个可运行的 Agent（三段拼接系统提示词）
- **`AgentManager`** + `agent_manager` 单例：按 slug 取 Agent
- **`/api/agent` 路由**

---

## [10] — 2026-08-27　Agent 配置系统：BaseContext

### 新增
- **`BaseContext`** dataclass：`thread_id` / `uid` / `model` / `system_prompt` / `tools` / `max_execution_steps` / `model_retry_times` / `summary_threshold` / `summary_keep_messages` / `tool_approval_mode`
- `ChatBotContext` 子类 + `update_from_dict`

---

## [9] — 2026-08-24　BaseAgent：LangGraph 图定义

### 新增
- **`BaseAgent`** 抽象基类：统一的图构建与流式调用接口
- `BaseState` + `merge_artifacts` reducer
- 首次接入 LangGraph `create_agent`
- checkpointer（`InMemorySaver`）实现多轮对话

---

## [8] — 2026-08-20　对话持久化：Thread 与 Message

### 新增
- **`conversations` / `messages` 表**
- **`ConversationRepository`**（Repository 模式）
- `GET /api/chat/threads`、`POST /api/chat/thread`、`GET /api/chat/thread/{id}/messages`
- 前端聊天页增加对话侧边栏

---

## [7] — 2026-08-17　流式 SSE：Token 逐字返回

### 新增
- **`POST /api/chat/stream`**：SSE 逐 token 返回
- `format_sse()` 工具
- 前端 `fetch` + `ReadableStream` 消费（因 `EventSource` 不支持自定义头）

---

## [6.5] — 2026-08-15　Git + GitHub

### 新增
- `.gitignore`（忽略 `.env`、`node_modules`、`__pycache__` 等）
- 项目接入版本控制，此后每版本收尾提交推送

---

## [6] — 2026-08-13　模型提供商：调用 LLM

### 新增
- **`LangChainChatAdapter`** + `select_model()`：统一模型调用入口
- 内置 SiliconFlow provider
- **`POST /api/chat/call`**：KK 第一次真正"说话"

---

## [5] — 2026-08-10　Vue 3 前端骨架 + 登录页

### 新增
- 前端工程（Vue 3 + Vite + Pinia + vue-router）
- 路由守卫（登录态判断）
- **`LoginView.vue`**
- `apis/base.js`：`apiGet` / `apiPost`（JWT 头 + 401 处理）

---

## [4] — 2026-08-06　用户注册与 JWT 认证

### 新增
- 密码哈希（argon2id）+ JWT 签发/验证
- **`POST /api/auth/register`** / **`POST /api/auth/token`** / **`GET /api/auth/me`**
- `get_current_user` / `get_required_user` 依赖

---

## [3] — 2026-08-03　PostgreSQL + SQLAlchemy

### 新增
- **`PostgresManager`**：引擎、会话池、`create_tables`
- **`users` 表**
- `backend/package/` 与 `backend/server/` 两层结构
- `GET /api/system/health`

---

## [2] — 2026-07-30　依赖管理与 FastAPI 入口

### 新增
- 13 个 Python 依赖 + `uv` 工作区
- FastAPI 应用 + CORS + router 汇总 + lifespan
- `uvicorn` reload 配置

---

## [1] — 2026-07-26　项目初始化 + Docker 开发环境

### 新增
- 3 容器：`api` + `web` + `postgres`
- `docker-compose.yml` + Dockerfile
- `.env` 配置（不提交）

---

> **关于本文件**：版本 1-17 为 2026-09-20 一次性回填（版本 17.7）。
> 从版本 18 起，每版本追加一条。
