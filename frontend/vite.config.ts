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
      },
      '/odds-api': {
        target: 'https://api.the-odds-api.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/odds-api/, '')
      },
      '/binance-api': {
        target: 'https://api.binance.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/binance-api/, '/api/v3')
      },
      '/fmp-api': {
        target: 'https://financialmodelingprep.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/fmp-api/, '')
      },
      '/api-sports-football': {
        target: 'https://v3.football.api-sports.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-sports-football/, '')
      },
      '/api-sports-americanfootball': {
        target: 'https://v1.american-football.api-sports.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-sports-americanfootball/, '')
      },
      '/api-sports-basketball': {
        target: 'https://v1.basketball.api-sports.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-sports-basketball/, '')
      },
      '/api-sports-baseball': {
        target: 'https://v1.baseball.api-sports.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-sports-baseball/, '')
      },
      '/api-sports-hockey': {
        target: 'https://v1.hockey.api-sports.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api-sports-hockey/, '')
      },
      '/sportmonks-api': {
        target: 'https://api.sportmonks.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sportmonks-api/, '')
      }
    }
  }
})
