<template>
    <el-scrollbar class="conversation-list">
        <el-empty 
            v-if="!conversations.length"
            description="暂无会话"
            :image-size="70"
        />
        <div 
            v-for="conv in conversations" 
            :key="conv.thread_id"
            class="conversation-item"
            :class="{ 'is-active': conv.thread_id === currentThreadId }"
            :title="conv.title"
            @click="$emit('select', conv.thread_id)"
        >
            {{ conv.title }}
        </div>
    </el-scrollbar>
</template>

<script setup>
defineProps({
    conversations: {type: Array, default: () => []},
    currentThreadId: {type: String, default: null},
})
defineEmits(['select'])
</script>

<style scoped>
.conversation-list {
    flex: 1;
    min-height: 0;      
}

.conversation-item {
    padding: 10px;
    border-radius: var(--kk-radius);
    color: #333;
    background: #fff;
    margin-bottom: 4%;
    cursor: pointer;
    border: rgba(255, 255, 255, 1);
    /* 防止文字超出宽度 */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.conversation-item:hover {
    background: #cecece;
}

.conversation-item.is-active {
    background: var(--kk-primary);
    font-weight: bold;
}
</style>