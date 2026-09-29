import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import '@/styles/reset.css'
import 'element-plus/dist/index.css'
import '@/styles/theme.css'
import 'dayjs/locale/zh-cn'



import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
    locale: zhCn,
})  // 配置 ElementPlus 为中文

app.mount('#app')