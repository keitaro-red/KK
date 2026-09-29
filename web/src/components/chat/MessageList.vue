对话消息列表
<template>
    <el-scrollbar ref="scrollRef" class="message-list">
        <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" />
        <div v-if="loading" class="message-list__hint">
            {{ runStatus === 'cancel_requested' ? '取消中...' : '思考中...' }}
        </div>
    </el-scrollbar>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({
    messages: Array,
    loading: Boolean,
    runStatus: String,
})

const scrollRef = ref(null)

// 滚动到最底部
async function scrollToBottom() {
    await nextTick()                        // 等 DOM 更新完再量高度
    const wrap = scrollRef.value?.wrapRef
    if (!wrap) return
    scrollRef.value.setScrollTop(wrap.scrollHeight)
}

//  列表被整个换掉 / 条数变了 —— 切换对话、新建对话、来了新消息
watch(() => [props.messages, props.messages.length], scrollToBottom)

//  最后一条的 content 在变 —— 流式追加 token，要一路跟着滚
watch(() => props.messages[props.messages.length - 1]?.content, scrollToBottom)
</script>

<style scoped>
.message-list {
    flex: 1;
    min-height: 0;
    font-size: 14px;
    background: linear-gradient(#ffffff44, #00000080),
        /* 背景图片，替换成你自己的图片地址 */
        url('@/assets/chat-backgound002.jpg') center / cover no-repeat;
}

.message-list :deep(.el-scrollbar__view){
    display: flex;
    padding: 24px;
    flex-direction: column;
    min-height: 100%;
    gap: 12px;
}

.message-list__hint {
    align-self: flex-start;
    padding: 6px 14px;
    border-radius: var(--kk-radius-lg);
    background: var(--kk-bubble-assistant);
    color: #fff;
}
</style>