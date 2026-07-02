import { createApp } from 'vue'
import './assets/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Configuración global de Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Interceptor para atrapar tokens inválidos (401)
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Si el backend dice que no estamos autorizados (token vencido o BD borrada)
      localStorage.removeItem('auth_token');
      delete axios.defaults.headers.common['Authorization'];
      // Redirigir al login usando el router
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

const app = createApp(App)
app.use(router)
app.mount('#app')
