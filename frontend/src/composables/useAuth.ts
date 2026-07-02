import { ref, computed } from 'vue';
import { clearUserCache } from './useUser';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Make sure to add token to axios defaults if it exists on load
const savedToken = localStorage.getItem('auth_token');
if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
}

export function useAuth() {
  const router = useRouter();
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!localStorage.getItem('auth_token'));

  const login = async (email: string, password: string) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.post('/api/login', { email, password });
      
      const token = response.data.access_token;
      if (token) {
        localStorage.setItem('auth_token', token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        return true;
      }
      return false;
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || 'Login failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };


  const logout = async () => {
    try {
      await axios.post('/api/logout');
    } catch (err) {
      console.error('Logout error', err);
    } finally {
      localStorage.removeItem('auth_token');
      delete axios.defaults.headers.common['Authorization'];
      clearUserCache();
      router.push('/login');
    }
  };

  return {
    login,
    logout,
    isLoading,
    error,
    isAuthenticated
  };
}
