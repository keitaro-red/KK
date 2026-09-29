<template>
    <div v-if="pending" class="approval-overlay">
        <div class="approval-dialog">
            <h3>工具审批</h3>
            <p>Agent 请求执行敏感操作：</p>
            <pre>{{ toolName }} {{ toolInput }}</pre>
            <div class="action-buttons">
                <button @click="decide('approve')">批准</button>
                <button @click="decide('reject')">拒绝</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'

const pending = ref(false)
const toolName = ref('')
const toolInput = ref('')

function show(toolCall){
    toolName.value = toolCall.toolName
    toolInput.value = JSON.stringify(toolCall.args,null,2)
    pending.value = true
}
async function decide(decision){
    pending.value = false
    // 发起 resume run ，带上 decision(run_type=resume)
    await resumeRun({decision,tool_call_id:currentToolCall.value    })
}
</script>
