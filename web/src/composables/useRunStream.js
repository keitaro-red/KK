import { useUserStore } from '@/stores/user'


/**
 * 消费一个 run 的 SSE 事件流
 * @param {string} runId - run运行ID
 * @param {object} handlers - 事件处理函数
 * @param {(text:string)=>void} handlers.onMessage - 收到一个token时调用
 * @param {(status:string,data:object)=>void} handlers.onEnd - 终态
 * @param {AbortSignal} [signal] - 用于组件卸载/切换时中断
 */
export async function useRunStream(runId, handlers = {}, signal) {
    const userStore = useUserStore()

    const resp = await fetch(`/api/agent/runs/${runId}/events`,
        {
            headers: { ...userStore.getAuthHeaders() },
            signal, // undefined 时，不中断
        }
    )

    // 检查响应状态
    if (!resp.ok) {
        throw new Error(`事件流订阅失败： ${resp.status}`)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
        while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const blocks = buffer.split('\n\n') // 按空行分割事件块
            buffer = blocks.pop() // 保留未处理完的事件块

            for (const block of blocks) {
                const lines = block.split('\n')
                const eventLine = lines.find((l) => l.startsWith('event: '))
                const dataLine = lines.find((l) => l.startsWith('data: '))
                if(!dataLine)continue
                const eventType = eventLine? eventLine.slice(7):'message'   // 'event: '七个字符
                const data = JSON.parse(dataLine.slice(6)) // 'data: '六个字符

                if(eventType==='message'&&data.content){
                    handlers.onMessage?.(data.content)
                }else if(eventType==='end'){
                    handlers.onEnd?.(data.status,data)
                    return      // 终态，结束循环
                }
                // 占位，tool_call/tool_result  interrupt
            }
        }
    }finally{
        // 提前return时，关闭reader
        reader.cancel().catch(()=>{})
    }
}




