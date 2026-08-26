<template>
    <div class="chat-page">
        <div class="chat-sidebar">
            <button class="new-chat-btn" @click="handleNewChat">+ 新对话</button>
            <div class="conversation-list">
                <div v-for="conv in conversations" :key="conv.thread_id"
                    :class="['conversation-item', { active: conv.thread_id === currentThreadId }]"
                    @click="handleSelectConversation(conv.thread_id)">
                    {{ conv.title }}
                </div>
            </div>
        </div>

        <div class="chat-main">
            <div class="chat-header">
                <h2>对话</h2>
                <button @click="handleLogout">退出登录</button>
            </div>
            <div class="chat-messages">
                <div v-for="(msg, i) in messages" :key=i :class="['message', msg.role]">
                    {{ msg.content }}
                </div>
                <div v-if="loading" class="message assistant">思考中...</div>
            </div>
            <div class="chat-input">
                <input v-model="input" type="text" placeholder="输入信息，回车发送" @keyup.enter="handleSend">
                    <button :disabled="loading" @click="handleSend">
                        {{ loading ? '发送中...' : '发送' }}
                    </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user'
import { apiGet, apiPost } from '../apis/base'

const router = useRouter()
const userStore = useUserStore()
const conversations = ref([])
const input = ref('')
const loading = ref(false)
const messages = ref([])
const currentThreadId = ref(null)

// const messages = ref([
//     { role: 'user', content: '你好，介绍一下你自己\n可以吗' },
//     { role: 'assistant', content: '你好！我是 AI 助手，有什么可以帮你的吗？' },
//     { role: 'user', content: '今天天气怎么样？' },
//     { role: 'assistant', content: '今天天气晴朗，气温 25-30 度，适合出门活动。' },
//     { role: 'user', content: '今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动' }
// ])
// const conversations = ref([{thread_id:1,title:'是的是是的是的是是的是的是的是的是的是的'}])



//获取当前用户的对话列表
async function loadConversations() {
    conversations.value = await apiGet('/api/chat/threads')
}

async function handleNewChat() {
    const data = await apiPost('/api/chat/thread')
    currentThreadId.value = data.thread_id
    messages.value = []
    input.value = ''
    await loadConversations()
}

async function handleSelectConversation(threadId) {
    currentThreadId.value = threadId
    messages.value = await apiGet(`/api/chat/thread/${threadId}/messages`)
}

// 旧非流式输出 
// async function handleSend() {
//     const text = input.value.trim()
//     if (!text || loading.value) return

//     messages.value.push({ role: 'user', content: text })
//     input.value = ''
//     loading.value = true

//     try {
//         const data = await apiPost('/api/chat/call', { query: text })
//         messages.value.push({ role: 'assistant', content: data.response })
//     } catch (error) {
//         messages.value.push({ role: 'assistant', content: `出错了：${error.message}` })
//     } finally {
//         loading.value = false
//     }
// }

async function handleSend() {
    const text = input.value.trim()
    if (!text || loading.value) return

    messages.value.push({ role: 'user', content: text })
    messages.value.push({ role: 'assistant', content: '' })
    input.value = ''
    loading.value = true

    // 发请求
    const body = { query: text }
    if (currentThreadId.value) body.thread_id = currentThreadId.value;
    try {
        const response = await fetch('/api/agent/runs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...userStore.getAuthHeaders(),
            },
            body: JSON.stringify(body),
        })

        if (!response.ok) {
            const err = await response.json()
            throw new Error(err.detail || `请求失败：${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        const lastMessage = messages.value[messages.value.length - 1]

        while (true) {
            const { done, value } = await reader.read()
            if (done) break;
            // 按空行切事件，最后一段返回buffer等补全
            buffer += decoder.decode(value, { stream: true })
            const parts = buffer.split('\n\n')
            buffer = parts.pop()

            for (const part of parts) {
                // 获取data字段
                const dataLine = part.split('\n').find((l) => l.startsWith('data: '))
                if (!dataLine) continue;
                // 去掉前面的data冒号空格6个字符
                const data = JSON.parse(dataLine.slice(6))
                if (data.content) {
                    lastMessage.content += data.content;
                }
                if (data.thread_id) {
                    currentThreadId.value = data.thread_id
                }
            }
        }
        await loadConversations()
    } catch (error) {
        messages.value.push({ role: 'assistant', content: `出错了：${error.message}` })
    } finally {
        loading.value = false
    }
}

function handleLogout() {
    userStore.logout()
    router.push('/login')
}

onMounted(loadConversations)
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.chat-page {
    display: flex;
    /* flex-direction: column; */
    height: 100vh;
    background: white;
}

.chat-sidebar {
    width: 240px;
    border-right: 2px solid #e3d894;
    display: flex;
    flex-direction: column;
    padding: 16px 12px;
    gap: 12px;
    background: linear-gradient(#455370);
}

.new-chat-btn {
    padding: 8px;
    background: #d3c782;
    color: black;
    border: 2px solid #e3d894;
    border-radius: 6px;
    cursor: pointer;
}

.new-chat-btn:hover {
    background: #f5ecb7;
}

.conversation-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.conversation-item {
    padding: 10px 10px;
    border-radius: 6px;
    color: #333;
    background: white;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
    font-size: 14px;
    border: rgba(255, 255, 255, 1);
}

.conversation-item:hover {
    background: #cecece;
}

.conversation-item:active {
    background: #e3d894;
}

.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* 头部 */
.chat-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 1.5% 24px;
    align-items: center;
    background: #3a3d62;
    /* margin-bottom: 24px; */
    border-bottom: 2px solid #e3d894;
    color: #e3d894;
}

.chat-header button {
    padding: 5px 8px;
    /* background: #f27c3b; */
    background: #e3d894;
    color: black;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
}

.chat-header button:hover {
    background: #f5ecb7;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    font-size: 13px;
    background: linear-gradient(#ffffff44, #00000080),
        /* 背景图片，替换成你自己的图片地址 */
        url('@/assets/chat-backgound002.jpg');
    /* 图片铺满整个区域，不变形 */
    background-size: cover;
    /* 图片居中显示 */
    background-position: center;
    /* 图片不重复平铺 */
    background-repeat: no-repeat;
    ;
}

.message {
    max-width: 75%;
    padding: 10px 18px;
    border-radius: 10px;
    line-height: 1.5;
    white-space: pre-wrap;
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(50px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.message.user {
    align-self: flex-end;
    background: #f27b3b44;
    color: white;

}

.message.assistant {
    align-self: flex-start;
    background: #ef979255;
    /* background: #e3d89444; */
    color: white;
}

.chat-input {
    display: flex;
    gap: 8px;
    padding: 6px 10px;
    border-top: 1px solid #e3d894;
    background: #455370;
}

.chat-input input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e3d894;
    border-radius: 6px;
    font-size: 13px;
}

.chat-input input:focus {
    border: black;
}

.chat-input button {
    padding: 5px 8px;
    background: #e3d894;
    color: black;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
}

.chat-input button:hover {
    background: #f5ecb7;
}

.chat-input button:disabled {
    background: #a8a16e;
    cursor: not-allowed;
}
</style>