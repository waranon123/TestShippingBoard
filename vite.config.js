import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Detect if it's production build (on Vercel)
const isProduction = process.env.NODE_ENV === 'production'

export default defineConfig({
  base: isProduction ? '/' : '/',  // ถ้า deploy ใน subfolder เช่น /frontend/ ให้ใส่ './'
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
