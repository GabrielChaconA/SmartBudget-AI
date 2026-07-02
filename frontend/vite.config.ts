import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Listen on all network interfaces for Docker
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true, // Necessary for some Windows/WSL/Docker setups
    },
    proxy: {
      '/api': {
        target: 'http://smartbudget_api',
        changeOrigin: true,
      },
      '/sanctum': {
        target: 'http://smartbudget_api',
        changeOrigin: true,
      }
    }
  }
})
