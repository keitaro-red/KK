<template>
    <div class="chat-page">
        <div class="chat-header">
            <h2>对话</h2>
            <button @click="handleLogout">退出登录</button>
        </div>
        <div class="chat-messages">
            <div v-for="(msg, i) in messages" :key=i :class="['message', msg.role]">
                {{ msg.content }}
                <div v-if="loading" class="message assistant">思考中...</div>
            </div>
        </div>
        <div class="chat-input">
                <input v-model="input" type="text" placeholder="输入信息，回车发送" @keyup.enter="handleSend">
                    <button :disabled="loading" @click="handleSend">
                        {{ loading ? '发送中...' : '发送' }}
                    </button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user'
import { apiPost } from '../apis/base'

const router = useRouter()
const userStore = useUserStore()

const input = ref('')
const loading = ref(false)
const messages = ref([])
// const messages = ref([
//   { role: 'user', content: '你好，介绍一下你自己\n可以吗' },
//   { role: 'assistant', content: '你好！我是 AI 助手，有什么可以帮你的吗？' },
//   { role: 'user', content: '今天天气怎么样？' },
//   { role: 'assistant', content: '今天天气晴朗，气温 25-30 度，适合出门活动。' },
//   {role:'user',content:'今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动'}
// ])

async function handleSend() {
    const text = input.value.trim()
    if (!text || loading.value) return

    messages.value.push({ role: 'user', content: text })
    input.value = ''
    loading.value = true

    try {
        const data = await apiPost('/api/chat/call', { query: text })
        messages.value.push({ role: 'assistant', content: data.response })
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
</script>

<style>
*{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
.chat-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: white;
}

.chat-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 1.5% 24px;
    align-items: center;
    background: #3a3d62;
    margin-bottom: 24px;
    border-bottom: 2px solid #e3d894;
    color: #e3d894;
}

.chat-header button {
    padding: 5px 8px;
    background: #f27c3b;
    color: white;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    font-size: 13px;
}
.message{
    max-width: 75%;
    padding: 10px 18px;
    border-radius: 10px;
    line-height: 1.5;
    white-space: pre-wrap;
}
.message.user{
    align-self: flex-end;
    background: #f27c3b;
    color: white;

}
.message.assistant{
    align-self: flex-start;
    /* background: #ef9792; */
    background: #e3d894;
    color: #333;
}
.chat-input{
    display: flex;
    gap:8px;
    padding: 6px 10px;
    border-top: 1px solid #e3d894;
    background: #455370;
}
.chat-input input{
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e3d894;
    border-radius: 6px;
    font-size: 13px;
}
.chat-input button {
    padding: 5px 8px;
    background: #f27c3b;
    color: white;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
}
.chat-input button:disabled {
    background: #ff910070;
    cursor: not-allowed;
}
</style>