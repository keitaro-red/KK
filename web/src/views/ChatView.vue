<template>
    <div class="chat-page">
        <ChatSidebar 
            :conversations="conversations" 
            :current-thread-id="currentThreadId" 
            @new="handleNewChat"
            @select="handleSelectConversation" 
        />
        <div class="chat-main">
            <ChatHeader @logout="handleLogout" />
            <MessagesList 
                :messages="messages" 
                :loading="loading" 
                :run-status="runStatus" 
            />
            <ChatComposer 
                :loading="loading" 
                @send="handleSend" 
                @cancel="handleCancel" 
            />
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user'
import { apiGet, apiPost } from '../apis/base'


import {useChatMessages} from '@/composables/useChatMessages'
import {useRunStream} from '@/composables/useRunStream'

import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import MessagesList from '@/components/chat/MessageList.vue'
import ChatComposer from '@/components/chat/ChatComposer.vue'


const router = useRouter()      // 路由
const userStore = useUserStore()      // 用户 store 

const {messages,pushUser, pushAssistant, replaceAll, clear ,fromHistory }=useChatMessages()


// ----- 对话列表相关 -----
const conversations = ref([])       // 用户对话列表
const currentThreadId = ref(null)       // 对话线程id


// ----- 运行状态相关 -----
const runStatus = ref('')       //运行状态
const activeRunId = ref(null)       //当前在跑的run的id
const loading = ref(false)      // 运行中



const input = ref('')       // 输入内容


// const conversations = ref([{thread_id:1,title:'是的是是的是的是是的是的是的是的是的是的'}])



//获取当前用户的对话列表
async function loadConversations() {
    conversations.value = await apiGet('/api/chat/threads')
}

// 创建新对话
async function handleNewChat() {
    const data = await apiPost('/api/chat/thread')
    currentThreadId.value = data.thread_id
    clear()
    await loadConversations()
}

// 选择对话
async function handleSelectConversation(threadId) {
    currentThreadId.value = threadId
    const raw = await apiGet(`/api/chat/thread/${threadId}/messages`)
    replaceAll(fromHistory(raw))
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

async function consume(runId,bubble){
    await useRunStream(runId,{
        onMessage:(text)=>{bubble.content += text},
        onEnd:(status,data)=>{
            if(status === 'failed'&& data.error){
                bubble.content += `\n[失败]${data.error}`
            }else if(status === 'cancelled'){
                bubble.content += '\n[已取消]'
            }
            // 成功时不用做，因为onMessage会自动添加
        }
    })
}


async function handleSend(text) {
    const query = (text||'').trim()
    if (!query || loading.value) return // 空消息或运行中，不处理

    pushUser(query)
    const bubble=pushAssistant()
    const lastMessage = messages.value[messages.value.length - 1]        // 记下带填充的信息
    loading.value = true
    runStatus.value = 'pending'

    // 发请求


    try {
        // 创建run POST秒回 {run_id, thread_id , status }
        const body = { query: text }
        if (currentThreadId.value) body.thread_id = currentThreadId.value;

        
        // 创建run
        const created = await apiPost('/api/agent/runs',body)
        activeRunId.value = created.run_id
        if (created.thread_id)
            currentThreadId.value = created.thread_id;

        // GET 订阅事件流
        await consume(created.run_id, bubble)
        await loadConversations()
    } catch (error) {
        bubble.content = `出错了：${error.message}`
    } finally {
        loading.value = false
        activeRunId.value = null
        runStatus.value = ''
    }
}


async function handleCancel() {
    if (!activeRunId.value) return
    await apiPost(`/api/agent/runs/${activeRunId.value}/cancel`)
    runStatus.value = 'cancel_requested'    // 取消中，处理完推 end:cancelled
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




.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}
</style>