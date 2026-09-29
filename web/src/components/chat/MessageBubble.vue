对话消息气泡
<template>
    <div :class="['message', message.role]">
        <div v-if="message.content" class="message__text">
            {{ message.content }}
        </div>
    </div>
</template>


<script setup>
defineProps({
    message: { type: Object, required: true }
})
</script>

<style scoped>
.message {
    font-size: 14px;
    max-width: 75%;
    padding: 10px 18px;
    border-radius: var(--kk-radius-lg);
    line-height: 1.5;
    white-space: pre-wrap;   /* 让\n换行 */
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(50px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.message.user {
    align-self: flex-end;
    background: var(--kk-bubble-user);
    color: white;

}

.message.assistant {
    align-self: flex-start;
    background: var(--kk-bubble-assistant);
    /* background: #e3d89444; */
    color: white;
}
</style>