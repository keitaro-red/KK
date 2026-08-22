# KK 智能体

参考 Yuxi 搭建的全栈多智能体平台，学建同步。

## 当前功能

- ✅ 用户注册 / 登录（JWT + argon2）
- ✅ LLM 对话（LangChain + 硅基流动 SiliconFlow，默认 DeepSeek）
- ✅ 对话持久化


## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.13 · FastAPI · SQLAlchemy · LangChain |
| 前端 | Vue 3 · Vite · Pinia |
| 存储 | PostgreSQL · Redis |
| 运行 | Docker Compose（4 容器） |

## 快速启动

```bash
cd KK
docker compose up -d --build
```

打开 http://localhost:5173 → 注册账号 → 登录 → 发一条消息试试。

## 项目结构

```
KK/
├── backend/   # FastAPI 后端
│   ├── server/    # API 路由 + 中间件
│   └── package/   # kk 业务包（config / models / storage）
├── web/       # Vue 3 前端
└── docker/    # 镜像构建文件
```