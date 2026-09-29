对话头
<template>
    <div class="chat-header">
        <h2 class="chat-header__title">对话</h2>
        <button class="chat-header__action" @click="onLogout">
            退出登录
        </button>
    </div>
</template>

<script setup>
import { ElMessageBox } from 'element-plus';

const emit = defineEmits(['logout']);

async function onLogout() {
    try{
        await ElMessageBox.confirm('确定退出登录吗？', '提示', {
            type: 'warning',
            confirmButtonText: '确定',
            cancelButtonText: '取消',
        })
    }catch{
        return
    }
    // 退出登录
    emit('logout')
}
</script>

<style scoped>
/* 头部 */
.chat-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 10px 24px;
    align-items: center;
    background: #3a3d62;
    /* margin-bottom: 24px; */
    border-bottom: 2px solid #e3d894;
    color: #e3d894;
}

.chat-header__title {
    font-size: 24px;
}

.chat-header__action {
    padding: 5px 8px;
    /* background: #f27c3b; */
    background: #e3d894;
    color: black;
    border: 2px solid #cdd2ad;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
}

.chat-header__action:hover {
    background: #f5ecb7;
}
</style>