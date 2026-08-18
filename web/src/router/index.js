import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from '@/stores/user'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/LoginView.vue'),
            meta: { requiresAuth: false },
        },
        {
            path: '/chat',
            name: 'chat',
            component: () => import('@/views/ChatView.vue'),
            meta: { requiresAuth: true },
        }
    ]
})
router.beforeEach((to)=>{
    const userStore = useUserStore()

    if (to.meta.requiresAuth && !userStore.isLoggedIn){
        return '/login'
    }

    if (to.path == '/login' && userStore.isLoggedIn){
        return '/chat'
    }


})

export default router