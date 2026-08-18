<template>
    <div class="login-page">
        <form class="login-form" @submit.prevent="handleLogin">
            <h1>登录 KK</h1>

            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

            <label>
                用户名
                <input v-model="username" type="text" placeholder="输入用户名" />
            </label>

            <label>
                密码
                <input v-model="password" type="password" placeholder="输入密码" />
            </label>

            <button type="submit" :disabled='loading'>
                {{ loading ? '登录中...' : '登录' }}
            </button>
        </form>
    </div>
</template>


<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
    if (!username.value || !password.value) {
        errorMessage.value = '请输入用户名和密码'
        return
    }
    try {
        loading.value = true
        errorMessage.value = ''
        await userStore.login(username.value, password.value)
        router.push('/chat')
    } catch (error) {
        errorMessage.value = error.message || '登录失败'
    } finally {
        loading.value = false
    }
}
</script>


<style scoped>
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #faf5ed;
}

.login-form {
    width: 360px;
    padding: 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 2px 3px rgba(0, 0, 0, 0.3);
}

.login-form h1 {
    text-align: center;
    margin: 0 0 8px 0;
    font-size: 28px;
}

.login-form label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 18px;
    color: #000000;
    margin-bottom: 5px;
}

.login-form input {
    padding: 10px 12px;
    border: 2px solid #969696;
    border-radius: 6px;
    font-size: 18px;
}
.login-form input:focus {
    outline: none;
    border-color: #f3b85f;
}
.login-form button {
    padding: 8px;
    background: #ffa42c;
    color: #ffffff;
    border: 2px solid #ffffff;
    border-radius: 10px;
    font-size: 18px;
    margin-top: 12px;
    cursor: pointer;
}
.login-form button:disabled {
    background: #ff910070;
    cursor: not-allowed;
}
.login-form button:hover:not(:disabled){
    background: #ff9100;
}
.error-message {
    padding: 10px 12px;
    background: #fff0f0;
    border:2px solid #ffd4d4;
    border-radius: 6px;
    font-size: 18px;
    color: #d44;
    text-align: center;
}
</style>