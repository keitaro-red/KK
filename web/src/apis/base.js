import { useUserStore } from "@/stores/user";

async function apiRequest(url, options = {}, requiresAuth = true) {
    const requestOptions = { ...options }

    if (requiresAuth) {
        const userStore = useUserStore()
        if (!userStore.isLoggedIn) throw new Error('用户未登录');
        requestOptions.headers = {
            ...requestOptions.headers,
            ...userStore.getAuthHeaders()
        }
    }

    if (!(options.body instanceof FormData)) {
        requestOptions.headers = {
            'Content-Type': 'application/json',
            ...requestOptions.headers
        }
    }
    const response = await fetch(url, requestOptions)

    if (!response.ok) {
        let detail = `请求失败：${response.status}`
        try {
            const errorData = await response.json()
            detail = errorData.detail || detail
        } catch { }

        if (response.status == 401) {
            const userStore = useUserStore()
            if (userStore.isLoggedIn) userStore.logout();
            window.location.href = '/login'
        }

        throw new Error(detail)
    }

    return response.json()
}

export function apiGet(url, options = {}, requiresAuth = true) {
    return apiRequest(url, { method: 'GET', ...options }, requiresAuth)
}
export function apiPost(url, data = {}, options = {}, requiresAuth = true) {
    const body = data instanceof FormData ? data : JSON.stringify(data)
    return apiRequest(url, { method: 'POST', body, ...options }, requiresAuth)
}