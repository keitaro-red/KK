# KK

一个全栈多智能体平台：**LangGraph Agent** + **FastAPI 后端** + **Vue 3 前端**，带工具调用、中间件栈、离线执行与流式输出。

> KK 是一个**学习项目**——通过 1:1 开发一个成熟的多智能体平台来掌握全栈开发。

---

## 技术栈

| 层 | 用什么 |
|---|---|
| 后端 | Python 3.13 · FastAPI · SQLAlchemy (async) · PostgreSQL 16 |
| Agent | LangGraph · LangChain · 中间件栈 · 工具系统 |
| 异步任务 | ARQ（基于 Redis 的任务队列）· Redis 7 |
| 前端 | Vue 3 · Vite · Pinia · vue-router · 原生 fetch（无 axios） |
| 容器 | Docker Compose（5 个服务） |
| 依赖管理 | uv |

---

## 快速开始

### 前置

- Docker Desktop（含 compose）
- 一个 SiliconFlow API Key（或兼容 OpenAI 协议的服务）

### 1. 配置文件

在仓库根目录建 `.env`：

```bash
# PostgreSQL
POSTGRES_USER=<自定义>
POSTGRES_PASSWORD=<自定义>
POSTGRES_DB=<自定义>
POSTGRES_URL=postgresql+asyncpg://<user>:<password>@postgres:5432/<db>

# Redis
REDIS_URL=redis://redis:6379/0

# 认证（生产环境必须显式设置，否则每个进程各自随机生成、token 互不认可）
JWT_SECRET_KEY=<自定义随机串>

# 模型
SILICONFLOW_API_KEY=<你的 API Key>

# 可选
KK_ENV=development                 # production 时 CORS 默认关闭，须配 KK_CORS_ORIGINS
KK_CORS_ORIGINS=                   # 逗号分隔，配了就覆盖默认
```

### 2. 起容器

```bash
docker compose up -d --build
```

5 个服务：

| 服务 | 容器名 | 端口 | 作用 |
|---|---|---|---|
| `api` | `kk-api-dev` | 5050 | FastAPI（uvicorn，reload 开启） |
| `worker-dev` | `kk-worker-dev` | — | ARQ worker，离线执行 Agent |
| `web` | — | 5173 | Vite dev server |
| `postgres` | `kk-postgres` | 5432 | 数据库 |
| `redis` | `kk-redis` | 6379 | 事件流 + 任务队列 |

> `api` 和 `worker-dev` **用同一个镜像、同一套挂载**，只有启动命令不同——这是这套架构的关键（见 `docs/ARCHITECTURE.md`）。

### 3. 验证

```bash
curl http://localhost:5050/api/system/health
# {"status":"ok","database":"connected"}
```

### 4. 跑通一条链路

```bash
# 注册（注册即登录，直接拿 token）
curl -X POST http://localhost:5050/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"12345678"}'

# 用返回的 access_token 发一条消息给 Agent
curl -X POST http://localhost:5050/api/agent/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query":"你好"}'
# → {"run_id":"...","thread_id":"...","status":"pending"}

# 订阅事件流
curl -N http://localhost:5050/api/agent/runs/<run_id>/events \
  -H "Authorization: Bearer <token>"
```

前端打开 <http://localhost:5173>。



---

## 目录结构

```
KK/
├── docker-compose.yml        5 个服务
├── .env                      配置（不提交）
├── docker/
│   ├── api.Dockerfile        Python 3.13 + uv
│   └── web.Dockerfile        Node + Vite
├── docs/                     ← 工程文档（见下方索引）
├── backend/
│   ├── pyproject.toml        uv 工作区
│   ├── server/               表现层：FastAPI 应用、路由、worker 入口
│   │   ├── main.py
│   │   ├── worker_main.py
│   │   ├── routers/          system / auth / chat / agent
│   │   └── utils/            lifespan、鉴权依赖
│   └── package/kk/           业务包（被两个进程共享）
│       ├── agents/           领域层：Agent、工具、中间件
│       ├── services/         服务层：用例编排
│       ├── repositories/     数据访问层
│       ├── models/           模型层
│       ├── storage/          基础设施层：Postgres / Redis / checkpointer
│       ├── utils/            横切工具
│       └── config.py
└── web/
    └── src/                  前端（views / components / stores / apis / router）
```

---

## 工程文档索引

| 文档 | 讲什么 |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 分层与依赖方向——新代码该写在哪一层 |
| [docs/API.md](docs/API.md) | **接口契约**——所有端点、鉴权、错误码、SSE 事件 |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | 表结构、关联、**状态机**、Redis 键空间、建表机制 |
| [docs/FRONTEND.md](docs/FRONTEND.md) | 前端规范——目录、请求层、路由、样式、命名 |
| [docs/DECISIONS.md](docs/DECISIONS.md) | **架构决策记录**——为什么这么选、否决过什么 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 每次改了什么 |

**新加入的话，建议阅读顺序**：本文件 → `ARCHITECTURE.md` → `API.md` → `DATA_MODEL.md`。

---

## 常用命令

```bash
# 起/停/重建
docker compose up -d
docker compose up -d --build
docker compose down

# 看日志
docker logs -f kk-api-dev
docker logs -f kk-worker-dev        # ← Agent 执行的输出在这里

# 进容器
docker exec -it kk-api-dev sh
docker exec -it kk-worker-dev sh

# 数据库
docker exec -it kk-postgres psql -U <user> -d <db>
docker exec -it kk-postgres psql -U <user> -d <db> -c "\dt"
docker exec -it kk-postgres psql -U <user> -d <db> -c "\d agent_runs"

# Redis
docker exec -it kk-redis redis-cli
docker exec -it kk-redis redis-cli keys 'run:*'
```

### ⚠️ 改了数据库模型之后

`create_all` **只建表、不改表**——改列不会自动生效。二选一：

```bash
# 删表重建（数据会没）
docker exec -it kk-postgres psql -U <user> -d <db> -c "DROP TABLE agent_runs;"
# 重启 api/worker 触发重建

# 或手工加列（保留数据）
docker exec -it kk-postgres psql -U <user> -d <db> -c "ALTER TABLE agent_runs ADD COLUMN xxx TEXT;"
```

KK **没有迁移框架**（无 Alembic）——这是已知技术债，见 `DECISIONS.md` ADR-010。

---

## 当前状态

**已跑通**：注册登录 → 对话持久化 → LLM 调用 → SSE 流式 → LangGraph Agent → 工具调用（含文件系统）→ ARQ 离线执行 → Run 生命周期（状态机/取消/查询）→ 中间件栈（压缩/重试/统计/附件）→ 工具审批。

---

## 开发约定

- **依赖方向单向**：上层依赖下层，下层绝不 import 上层（详见 `docs/ARCHITECTURE.md`）
- **业务逻辑进服务层**，router 只做收参/鉴权/返回
- **前端请求走 `apis/`**，不裸 `fetch`（详见 `docs/FRONTEND.md`）
- **改接口/表/前端约定时，同步更新 `docs/`**——文档和代码必须一致
- **`.env` 永不提交**，任何密钥不进代码、不进日志
