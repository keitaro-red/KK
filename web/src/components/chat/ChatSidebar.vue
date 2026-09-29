对话侧边栏
<template>
    <aside class="chat-sidebar" :class="{'is_collapsed':collapsed}">
        <div class="chat-sidebar__head">
            <el-button
                class="chat-sidebar__toggle"
                text
                @click="collapsed = !collapsed"
            >
                <el-icon v-if="!collapsed"><Expand /></el-icon>
                <el-icon v-else><Fold /></el-icon>
            </el-button>
            <el-button
                class="chat-sidebar_new"
                v-if="!collapsed"
                @click="$emit('new')"
            >
                <el-icon><Plus /></el-icon>
                新对话
            </el-button>
        </div>

        <ConversationList
            v-show="!collapsed"
            :conversations="conversations"
            :current-thread-id="currentThreadId"
            @select="$emit('select', $event)"
        />
    </aside>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, Expand, Fold } from '@element-plus/icons-vue'
import ConversationList from './ConversationList.vue'

defineProps({conversations:Array,currentThreadId:String})
defineEmits(['new','select'])

const collapsed = ref(false)
</script>

<style scoped>
.chat-sidebar {
    width: 200px;
    display: flex;
    flex-direction: column;
    padding: 16px 12px;
    gap: 12px;
    background:var(--kk-bg-sidebar);
    border-right: 2px solid var(--kk-primary);
    transition:width 0.2s ease;
    overflow-x: hidden;
}
.chat-sidebar.is_collapsed {
    padding: 16px 0px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 48px;
}

.chat-sidebar__head {
    display: flex;
    align-items: space-between;
    gap: 6px;
}

.chat-sidebar_new {
    padding: 8px;
    background: #d3c782;
    color: white;
    border: 2px solid #e3d894;
    cursor: pointer;
}

.chat-sidebar_new:hover {
    background: #f5ecb7;
}

.chat-sidebar__toggle {
    /* text 按钮：去掉边框，只留图标 */
    --el-button-text-color:white;
    background: var(--kk-primary);
    --el-button-hover-text-color: var(--kk-primary-hover);
    flex-shrink: 0;
}
</style>