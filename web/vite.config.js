import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve:{
    alias:{
      '@':resolve(__dirname,'src')
    }
  },
  server:{
    watch: {
      usePolling: true,     // 用轮询代替文件监听
      interval: 1000        // 每 1 秒检查一次
    },
    proxy:{
      '^/api':{
        target:'http://api:5050',
        changeOrigin:true
      }
    }
  }
})
