import { ref ,reactive} from 'vue'

let seq = 0
function newId() {
    // 随机ID生成
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
    }
    return `m_${Date.now()}_${seq++}`
}

export function useChatMessages() {
    const messages = ref([])

//     const messages = ref([
//     { role: 'user', content: '你好，介绍一下你自己\n可以吗' },
//     { role: 'assistant', content: '你好！我是 AI 助手，有什么可以帮你的吗？' },
//     { role: 'user', content: '今天天气怎么样？' },
//     { role: 'assistant', content: '今天天气晴朗，气温 25-30 度，适合出门活动。' },
//     { role: 'user', content: '今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动今天天气晴朗，气温 25-30 度，适合出门活动' }
// ])


    // 创建新消息
    function createMessage(role, content = '') {
        return reactive({
            id: newId(),
            role,
            content,
            toolCalls: [],
        })
    }

    // 推送用户消息
    function pushUser(content) {
        const msg = createMessage('user', content)
        messages.value.push(msg)
        return msg
    }

    // 推送AI助手消息
    function pushAssistant() {
        const msg = createMessage('assistant')
        messages.value.push(msg)
        return msg
    }

    // 替换所有消息
    function replaceAll(list) {
        messages.value = list
    }

    // 清空所有消息
    function clear() {
        messages.value = []
    }

    function fromHistory(rawlist) {
        return (rawlist || []).map((raw)=>({
            id: newId(),
            role: raw.role,
            content: raw.content,
            toolCalls: [],
        }))
    }

    return { messages, pushUser, pushAssistant, replaceAll, clear ,fromHistory}
}