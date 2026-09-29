<template>
    <div class="chat-composer">
        <el-input
            v-model="draft"
            class="chat-composer__field"
            type="textarea"
            :autosize="{minRows:2,maxRows:6}"
            resize="none"
            placeholder="Shift+Enter 换行，Enter 发送"
            @keydown.enter="onEnter" 
        />

        <el-button
            v-if="!loading"
            class="chat-composer__action"
            type="primary"
            @click="submit"
        >
            发送
        </el-button>
        <el-button
            v-else
            class="chat-composer__action"
            type="danger"
            @click="$emit('cancel')"
        >
            取消
        </el-button>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({loading:Boolean})
const emit=  defineEmits(['send','cancel'])

const draft = ref('')

function submit() {
    const text = draft.value.trim() // 去掉首尾空格
    if (!text || props.loading) return

    emit('send', text)
    draft.value = ''
}

function onEnter(e) {
    if (e.shiftKey) return

    e.preventDefault() // 阻止默认换行
    submit()    // 发送消息
}

</script>


<style scoped>
.chat-composer {
    display: flex;
    gap: 8px;
    padding: 6px 10px;
    border-top: 1px solid #e3d894;
    background: #455370;
}

.chat-composer__field {
    flex: 1;
    border: 1px solid #e3d894;
    border-radius: 6px;
    font-size: 13px;
}

.chat-composer__field:focus {
    border: black;
}

.chat-composer__action {
    padding: 5px 8px;
    background: #e3d894;
    color: white;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 14px;
    cursor: pointer;
}

.chat-composer__action:hover {
    background: #f5ecb7;
}

.chat-composer__action:disabled {
    background: #a8a16e;
    cursor: not-allowed;
}
</style>