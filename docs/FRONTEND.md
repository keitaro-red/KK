# KK 前端规范

> **本文档回答**：我要加个新页面/组件，应该放哪、怎么写、跟谁保持一致？
> **最后更新**: 2026-09-20（版本  17.7）
>
> **注意**：本文档的"规范"部分是从**现有代码里归纳**的，不是从网上抄的通用规范。代码里**不统一的地方**如实记在第八节——那不是规范，是**待统一的债**。

---

## 一、技术栈

| 项 | 用什么 | 版本（以 `web/package.json` 为准） |
|---|---|---|
| 框架 | Vue 3（**只用 `<script setup>`**） | `^3.5.40` |
| 构建 | Vite + `@vitejs/plugin-vue` | `^8.2.0` / `^6.0.8` |
| 语言 | **JavaScript（没有 TypeScript）** | — |
| 状态 | Pinia（setup 写法） | `^4.0.2` |
| 路由 | vue-router（**HTML5 History 模式**） | `^5.2.0` |
| HTTP | **原生 `fetch`（没有 axios）** | — |
| 样式 | 原生 CSS + **CSS 变量**（无预处理器、无原子化框架） | - |
| UI 组件库 | **Element Plus**（**全量引入**） | `^2.x` |
| 图标 | `@element-plus/icons-vue` | `^2.x` |
| Lint / Format | **暂无**（无 eslint/prettier 配置，无 lint 脚本） | 见第八节 |
| 测试 | **暂无** | 版本 33  |

**路径别名**：`@` → `web/src`（配置在 `vite.config.js`）。

---

## 二、目录结构

```
web/src/
├── main.js              创建 app、装 pinia 与 router、mount('#app')
├── App.vue              根组件，只有 <router-view />
├── apis/                请求层（见第四节）
│   └── base.js          apiRequest / apiGet / apiPost
├── assets/              静态资源（图片）
├── components/          可复用组件
│   └── ApprovalDialog.vue   工具审批弹窗（**未接线**，见第九节）
├── router/
│   └── index.js         路由表 + 登录守卫
├── stores/
│   └── user.js          用户 store（token / 用户信息 / login / logout）
└── views/               页面级组件（**统一 `XxxView.vue` 命名**）
│   ├── LoginView.vue
│   └── ChatView.vue
├── styles/            全局样式（reset / theme）
├── composables/       组合式函数（可复用逻辑）
└── components/chat/   聊天页拆出的组件
```

**没有**：`src/api/`（是 `apis`，复数）、`src/utils/`、`src/layouts/。

**约定**：
- 页面放 `views/`，命名 `XxxView.vue`
- 可复用组件放 `components/`
- 目录名全小写

---

## 三、路由

`web/src/router/index.js`：

| 路径 | name | 组件 | meta |
|---|---|---|---|
| `/login` | `login` | `LoginView.vue` | `{ requiresAuth: false }` |
| `/chat` | `chat` | `ChatView.vue` | `{ requiresAuth: true }` |

**守卫逻辑**：
- `requiresAuth` 且未登录 → 跳 `/login`
- 已登录访问 `/login` → 跳 `/chat`

**登录态怎么判断**：`userStore.isLoggedIn` = `!!token`，`token` 初值取 `localStorage.getItem('user_token')`。

> ⚠️ **只判断 token 字符串非空**，不校验有效性、不调后端 `/api/auth/me`。过期的 token 会被放行，直到某个请求返回 401 才被踢出去。

**已知空白**（见第九节）：没有根路径 `/` 重定向、没有 404 兜底路由。

---

## 四、请求层（`apis/`）

### 唯一的封装：`apis/base.js`

| 函数 | 签名 |
|---|---|
| `apiGet` | `apiGet(url, options = {}, requiresAuth = true)` |
| `apiPost` | `apiPost(url, data = {}, options = {}, requiresAuth = true)` |

`apiRequest` 是内部核心函数，**不导出**。

### 它自动做了什么

| 行为 | 细节 |
|---|---|
| **加 JWT 头** | `requiresAuth=true` 时自动加 `Authorization: Bearer <token>`（来自 `userStore.getAuthHeaders()`） |
| 未登录时 | 直接 `throw new Error('用户未登录')`，**不跳转**（靠路由守卫兜底） |
| **Content-Type** | 非 `FormData` 时自动 `application/json`；`apiPost` 自动 `JSON.stringify` |
| **错误提取** | 非 2xx 时取后端 `detail` 字段作为错误消息，兜底 `请求失败：{status}` |
| **401 处理** | 清 token + `window.location.href = '/login'`（**整页硬跳转**），然后继续 throw |

### Base URL 从哪来

**前端没有环境变量机制**（`web/` 下没有 `.env*`，代码里没有 `VITE_*`）。开发期靠 **Vite 代理**：

```js
// vite.config.js
proxy: { '^/api': { target: 'http://api:5050', changeOrigin: true } }
```

即前端一律请求 `/api/...`，由 dev server 转发到容器 `api:5050`。

> ⚠️ **生产构建没有 base URL 方案**——这是当前最主要的架构空白，版本 35 （生产部署）要解决。

### 规范（新代码必须遵守）

1. **业务端点必须走 `apiGet` / `apiPost`**，不要裸 `fetch`。
2. **URL 一律以 `/api/` 开头**（带前导斜杠），不要写 `api/...`。
3. **端点 URL 集中在 `apis/` 下按资源分文件**（如 `apis/agent.js`），不散落在 view 里。

> ⚠️ **现状未达标**：登录（`stores/user.js`）、创建 run、SSE 三处是裸 `fetch`；URL 前缀 `/api` 与 `api` 混用；`apis/` 下只有 `base.js`。详见第八节。

---

## 五、SSE 流式消费

### 用 `fetch` + `ReadableStream`，不用 `EventSource`

代码里的原因写得很清楚（`views/ChatView.vue`）：

```js
// EventSource 不能带 Authorization 头，仍用 fetch + ReadableStream
```

**`EventSource` 不支持自定义请求头**，而我们的接口要 `Authorization: Bearer`。所以只能用 `fetch` 拿 `response.body.getReader()`，手工解析 SSE 帧。

### 解析算法（手工实现）

```js
const blocks = buffer.split('\n\n')   // 按空行切事件帧
buffer = blocks.pop()                 // 最后一段不完整，留到下一轮
for (const block of blocks) {
    const eventLine = lines.find(l => l.startsWith('event: '))
    const dataLine  = lines.find(l => l.startsWith('data: '))
    const eventType = eventLine ? eventLine.slice(7) : 'message'
    const data = JSON.parse(dataLine.slice(6))
}
```

- 帧分隔符：`\n\n`
- 字段前缀：`event: `（`slice(7)`）、`data: `（`slice(6)`）
- 没写 `event:` 时默认类型 `'message'`
- **未处理** SSE 的 `id:` / `retry:` / 注释行 / 多行 `data:` 合并——简化版，对当前后端够用

### 事件类型

| event | payload | 前端行为 |
|---|---|---|
| `message` | `{content}` | 追加到当前 assistant 消息（逐 token 流式渲染） |
| `end` | `{status}` | 结束消费；`failed` 追加 `[失败] {error}`，`cancelled` 追加 `[已取消]` |
| 其它 | — | 静默忽略 |

### 流式渲染技巧

发送时**先 push 一条空的 assistant 消息**并记住它的引用，之后靠**引用原地追加** `content` 实现流式效果——不用每次重建数组。

### 取消是"服务端语义"

前端 `POST /api/agent/runs/{id}/cancel`，**不中断本地读取循环**，继续等后端推 `end`（`status=cancelled`）。

> ⚠️ **全项目没有 `AbortController`**：没有超时中断，组件卸载时也没有 `reader.cancel()`。如果后端永远不推 `end`，`loading` 会永久卡住。详见第八节。

---

## 六、组件清单

| 文件 | 职责 |
|---|---|
| `views/LoginView.vue` | 登录页 |
| `views/ChatView.vue` | 聊天页**编排层**（状态 + 组装） |
| `components/chat/ChatSidebar.vue` | 侧边栏容器（**可收起**） |
| `components/chat/ConversationList.vue` | 会话列表 |
| `components/chat/ChatHeader.vue` | 顶栏 + 退出登录 |
| `components/chat/MessageList.vue` | 消息滚动区 + 自动到底 |
| `components/chat/MessageBubble.vue` | 消息气泡（手写） |
| `components/chat/ChatComposer.vue` | 输入区 |
| `composables/useChatMessages.js` | 消息数据结构 + 操作 |
| `composables/useRunStream.js` | SSE 流消费（零状态） |
| `styles/reset.css` / `theme.css` | 全局样式基线 |

---

## 七、编码规范（新代码必须遵守）

### 已形成一致的约定（照做）

| 维度 | 约定 |
|---|---|
| API 风格 | **`<script setup>`**，不用 Options API / `defineComponent` |
| 组件文件名 | **PascalCase**（`ChatView.vue`） |
| 页面命名 | 统一 `XxxView.vue` |
| 非组件文件名 | **全小写**（`base.js`、`index.js`） |
| 变量 | **camelCase**；ref 不加 `is/has` 前缀（用 `loading`，不用 `isLoading`） |
| 事件处理器 | **`handleXxx`**（`handleSend` / `handleCancel` / `handleLogin`） |
| 取数函数 | **`loadXxx`**（`loadConversations`） |
| store | `defineStore('user', ...)` 的 id 与文件名一致，导出 `useUserStore` |
| 缩进 | **4 空格** |
| 注释 | **中文**，解释"为什么"而非"做了什么" |

### 待确认后写（目前代码里不一致）

以下几条代码里是混着的，**建议统一，但需要你拍板**：

| 项 | 定案 |
|---|---|
| 分号 | **用**（与 `apis/base.js` 一致） |
| 字符串引号 | 单引号 |
| 模块路径 | **统一 `@/`**，跨目录不写相对路径 |
| 模板属性引号 | 双引号 |
| **裸标签选择器** | **禁止**——只写类名（`button` / `input` / `div` 一律不裸用） |
| `<style>` | **一律 `scoped`**；全局样式只放 `styles/` |
| 状态归属 | **能下沉就下沉**；只有容器组件能 import api / store |

> ⚠️ 上面"待确认"的几条，在你拍板前**新代码请按"建议"列写**——至少不要再增加分歧。

---

## 八、待统一 / 技术债（如实记录现状）

这些是**已经存在**的问题，不是规范。写在这里是为了：将来动手时知道有什么、不要新增同类。

| # | 问题 | 位置 | 影响 |
|---|---|---|---|
| 2 | 业务端点绕过 `apis/` 封装，裸 `fetch` | `stores/user.js`（login / me）、`views/ChatView.vue`（创建 run） | 401 处理、错误提取逻辑重复且不一致 |
| 3 | URL 前缀混用 `/api/auth/token` 与 `api/auth/token` | `stores/user.js` | 相对路径解析，脆弱 |
| 4 | **没有 `AbortController`**：无超时、组件卸载不取消读取 | `views/ChatView.vue` | 流永不 `end` 时 `loading` 永久卡住；组件销毁后仍在读 |
| 5 | SSE 消费**没检查 `response.ok`** | `views/ChatView.vue` | 非 2xx 时把错误响应体当 SSE 解析，静默失败 |
| 6 | `apiRequest` 结尾无条件 `response.json()` | `apis/base.js` | 返回 204 / 空 body 会抛 JSON 解析错误 |
| 7 | 没有根路径 `/` 重定向、没有 404 兜底路由 | `router/index.js` | 访问 `/` 白屏 |
| 8 | 登录态只判断 token 非空、不校验有效性 | `stores/user.js` | 过期 token 放行，直到 401 才踢 |
| 9 | **无 lint / format 配置**，无对应 npm 脚本 | `web/` | 风格靠自觉，必然继续分歧 |
| 10 | 死代码保留（注释掉的假数据、旧非流式实现） | `views/ChatView.vue` | 噪音 |
| 11 | 零星错误：无效 CSS 声明（`border: rgba(...)` 缺宽度）、变量名笔误 `reap`（应为 `resp`）、未使用的 import | 多处 | 小问题，顺手修 |
| 12 | Token 存 localStorage（XSS 可读），无 httpOnly 方案 | `stores/user.js` | 安全权衡，见 `DECISIONS.md` |

---

## 九、已知空白（尚未实现）

| 空白 | 说明 | 哪版本 |
|---|---|---|
| **`ApprovalDialog.vue` 未接线** | 目前是半成品：没有被任何地方 import；内部 `show()` 没有 `defineExpose` 也没有 props，父组件无法打开它；`decide()` 调用了**未定义的 `resumeRun` 和 `currentToolCall`**；模板用了三个类名但**完全没有样式** | 第 17 版本 /  17.5（后端 resume 打通后接线） |
| **前端 env 机制** | 生产构建的 base URL 无方案 | 版本 35  |
| **组件库** | 目前全部 UI 手写 CSS | 版本 17.6 |
| 会话列表的搜索 / 置顶 / 归档 / 删除 | — | 版本 43 / 49  |
| 工作区文件管理界面 | — | 版本 42  |
| Markdown 渲染 / 代码高亮 | 消息目前是纯文本 | 版本 43  |

---

## 十、组件库（待定）

> **Element Plus**，**全量引入**（`app.use(ElementPlus, { locale: zhCn })`）。
> - 主题定制：`styles/theme.css` 里覆盖 `--el-color-primary` 及**全部衍生色**（`light-3/5/7/8/9`、`dark-2`）——只改主色会导致 hover 仍是默认蓝
> - 图标：`@element-plus/icons-vue`，用 `<el-icon><Plus /></el-icon>` 包裹
> - 中文：`app.use` 传 `zhCn` + `import 'dayjs/locale/zh-cn'`（**日期组件必须单独引 dayjs 语言包**）
> - 未来若 Vite 8 生态明确，可评估改按需引入