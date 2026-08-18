import { ref, computed } from "vue"
import { defineStore } from "pinia"

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('user_token') || '')
    const userId = ref(null)
    const username = ref('')
    const uid = ref('')
    // 计算属性
    const isLoggedIn = computed(()=>!!token.value)
    // 方法
    async function login(loginId,password) {
        const formData = new FormData()
        formData.append('username',loginId)
        formData.append('password',password)

        const response = await fetch('api/auth/token',{
            method:'POST',
            body:formData,
        })

        if(!response.ok){
            const error =await response.json()
            throw new Error(error.detail|| '登录失败')
        }

        const data =await response.json()

        token.value = data.access_token
        userId.value = data.user_id
        username.value =data.username
        uid.value=data.uid

        localStorage.setItem('user_token',data.access_token)
    }

    function logout(){
        token.value=''
        userId.value=null
        username.value=''
        uid.value=''
        localStorage.removeItem('user_token')
    }

    async function getCurrentUser(){
        const response = await fetch('/api/auth/me',{
            headers:{Authorization:`Bearer ${token.value}`}
        })
        if(!response.ok) throw new Error('获取用户信息失败')
        
        const data=await response.json()
        userId.value =data.id
        username.value=data.username
        uid.value=data.uid
        return data
    }

    function getAuthHeaders(){
        return {Authorization:`Bearer ${token.value}`}
    }

    return {token,userId,username,uid,isLoggedIn,login,logout,getCurrentUser,getAuthHeaders}
})