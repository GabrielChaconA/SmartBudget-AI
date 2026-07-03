import { ref, onMounted } from 'vue';
import axios from 'axios';

export interface UserProfile {
  id?: number;
  name?: string;
  email?: string;
  avatar?: string;
  currency?: string;
  monthlyIncome?: number;
  [key: string]: any;
}

// Global state outside the composable so it acts as an in-memory cache
const user = ref<UserProfile | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const isInitialized = ref(false);

export function clearUserCache() {
  user.value = null;
  error.value = null;
  isInitialized.value = false;
  isLoading.value = false;
}

export function useUser() {
  const fetchUser = async () => {
    if (isInitialized.value) return;
    
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get('/api/user');
      user.value = response.data;
      isInitialized.value = true;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch user data';
      console.error('Error fetching user:', err);
    } finally {
      isLoading.value = false;
    }
  };

  const createFund = async (data: { name: string, balance: number, color?: string, icon?: string }) => {
    try {
      const res = await axios.post('/api/funds', data);
      if (user.value) {
        user.value.funds.push({
          id: res.data.id,
          ...data,
          allocations: []
        });
      }
      return true;
    } catch (err) {
      console.error('Error creating fund', err);
      return false;
    }
  };

  const updateFund = async (id: number, data: { name?: string, balance?: number }) => {
    try {
      await axios.put(`/api/funds/${id}`, data);
      if (user.value) {
        const index = user.value.funds.findIndex((f: any) => f.id === id);
        if (index !== -1) {
          user.value.funds[index] = { ...user.value.funds[index], ...data };
        }
      }
      return true;
    } catch (err) {
      console.error('Error updating fund', err);
      return false;
    }
  };

  const allocateFund = async (fundId: number, categoryName: string, amount: number) => {
    try {
      await axios.post(`/api/funds/${fundId}/allocations`, { category_name: categoryName, amount });
      if (user.value) {
        const fund = user.value.funds.find((f: any) => f.id === fundId);
        if (fund) {
          fund.allocations.push({ category_name: categoryName, amount });
          fund.balance = (parseFloat(fund.balance) + parseFloat(amount.toString())).toString();
        }
      }
      return true;
    } catch (err) {
      console.error('Error allocating fund', err);
      return false;
    }
  };

  const fetchIncomeStats = async () => {
    try {
      const response = await axios.get('/api/user/income-stats');
      return response.data;
    } catch (err) {
      console.error('Error fetching income stats:', err);
      return [];
    }
  };

  const searchSubscriptionCatalog = async (query: string) => {
    try {
      const response = await axios.get(`/api/subscription-catalog?query=${encodeURIComponent(query)}`);
      return response.data;
    } catch (err) {
      console.error('Error searching catalog', err);
      return [];
    }
  };

  const addSubscription = async (data: any) => {
    try {
      const response = await axios.post('/api/subscriptions', data);
      if (user.value) {
        // Mock a status and category for UI immediately
        user.value.subscriptions.push({
          ...data,
          id: response.data.id,
          status: 'active',
        });
      }
      return true;
    } catch (err) {
      console.error('Error adding subscription', err);
      return false;
    }
  };

  const addInvestment = async (data: any) => {
    try {
      const response = await axios.post('/api/investments', data);
      if (user.value) {
        if (!user.value.investments) {
          user.value.investments = [];
        }
        user.value.investments.push({
          ...data,
          id: response.data.id,
        });
      }
      return true;
    } catch (err) {
      console.error('Error adding investment', err);
      return false;
    }
  };

  const updateProfile = async (data: { name?: string, avatar?: string }) => {
    try {
      await axios.put('/api/user/profile', data);
      if (user.value) {
        if (data.name) user.value.name = data.name;
        if (data.avatar) user.value.avatar = data.avatar;
      }
      return true;
    } catch (err) {
      console.error('Error updating profile', err);
      return false;
    }
  };

  const uploadAvatar = async (file: File) => {
    try {
      const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
      const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET;
      
      if (!cloudName || !uploadPreset) {
        console.error('Cloudinary credentials missing');
        return false;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('upload_preset', uploadPreset);

      isLoading.value = true;
      const res = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/image/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      
      if (data.secure_url) {
        await updateProfile({ avatar: data.secure_url });
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error uploading avatar', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  };


  onMounted(() => {
    fetchUser();
  });

  return {
    user,
    isLoading,
    error,
    fetchUser,
    createFund,
    updateFund,
    allocateFund,
    fetchIncomeStats,
    searchSubscriptionCatalog,
    addSubscription,
    updateProfile,
    uploadAvatar,
    addInvestment
  };
}
