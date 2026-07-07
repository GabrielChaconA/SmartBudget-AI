import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { exchangeRateService } from '@/services/exchangeRate';

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
const isBalancesVisible = ref(true);
const hiddenBalances = ref<Record<string, boolean>>({});
const notifications = ref<any[]>([]);
const globalExchangeRate = ref(20.0);
const liveInvestmentsAmount = ref<number | null>(null);

import { finnhubService } from '@/services/finnhub';
import { oddsApiService } from '@/services/oddsApi';

export function clearUserCache() {
  user.value = null;
  error.value = null;
  isInitialized.value = false;
  isLoading.value = false;
}

export function useUser() {
  const fetchLiveInvestmentsAmount = async () => {
    if (!user.value?.investments || user.value.investments.length === 0) {
      liveInvestmentsAmount.value = 0;
      return;
    }
    try {
      const etfs = user.value.investments.filter((i: any) => i.type === 'etfs');
      const stocks = user.value.investments.filter((i: any) => i.type === 'stocks');
      const cryptos = user.value.investments.filter((i: any) => i.type === 'crypto');
      const bets = user.value.investments.filter((i: any) => i.type === 'bets');
      
      const cryptoIds = cryptos.map((c: any) => c.symbol.toLowerCase());

      // Per-symbol safe fetch — one failure doesn't wipe everything out
      const fetchQuoteSafe = async (h: any) => {
        try {
          const q = await finnhubService.getQuote(h.symbol);
          return { h, q };
        } catch {
          return { h, q: { c: h.average_price || 0, dp: 0, d: 0, h: 0, l: 0, o: 0, pc: 0 } };
        }
      };
      
      const [etfRes, stockRes, cryptoRes, oddsRes] = await Promise.allSettled([
        Promise.all(etfs.map(fetchQuoteSafe)),
        Promise.all(stocks.map(fetchQuoteSafe)),
        cryptoIds.length > 0 ? coingeckoService.getMarkets(cryptoIds) : Promise.resolve([]),
        oddsApiService.getUpcomingOdds()
      ]);
      
      let totalVal = 0;
      const userCurrency = user.value?.currency || 'MXN';
      
      const processVal = (h: any, currentPrice: number) => {
        if (!currentPrice || currentPrice <= 0) return;
        let val = h.quantity * currentPrice;
        if (h.currency === 'USD' && userCurrency === 'MXN') val *= globalExchangeRate.value;
        if (h.currency === 'MXN' && userCurrency === 'USD') val /= globalExchangeRate.value;
        totalVal += val;
      };
      
      if (etfRes.status === 'fulfilled') {
        etfRes.value.forEach((item: any) => processVal(item.h, item.q.c));
      }
      if (stockRes.status === 'fulfilled') {
        stockRes.value.forEach((item: any) => processVal(item.h, item.q.c));
      }
      if (cryptoRes.status === 'fulfilled' && cryptoRes.value.length > 0) {
        cryptos.forEach((h: any) => {
          const market = cryptoRes.value.find((m: any) => m.symbol.toLowerCase() === h.symbol.toLowerCase());
          processVal(h, market?.current_price || h.average_price);
        });
      } else {
        // fallback: use average_price when CoinGecko fails
        cryptos.forEach((h: any) => processVal(h, h.average_price));
      }
      if (oddsRes.status === 'fulfilled' && oddsRes.value.length > 0) {
        bets.forEach((h: any, index: number) => {
          const event = oddsRes.value[index % oddsRes.value.length];
          const homeOdds = event?.bookmakers?.[0]?.markets?.[0]?.outcomes?.[0]?.price || 1.0;
          processVal(h, homeOdds);
        });
      } else {
        bets.forEach((h: any) => processVal(h, h.average_price || 1));
      }
      
      liveInvestmentsAmount.value = totalVal;
    } catch (e) {
      console.error('Error fetching live investments', e);
      // Don't reset liveInvestmentsAmount — keep the last known value
    }
  };

  const fetchUser = async (force = false) => {
    if (isInitialized.value && !force) {
      fetchLiveInvestmentsAmount();
      return;
    }
    
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get('/api/user');
      user.value = response.data;
      isInitialized.value = true;
      // Auto-fix: sync Cartera balance with sum of funds (fixes negative free money)
      axios.post('/api/reset-free-money').catch(() => {});
      exchangeRateService.getUsdMxnRate().then(rate => {
        globalExchangeRate.value = rate;
        fetchLiveInvestmentsAmount();
      }).catch(() => {});
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

  const allocateFund = async (fundId: number, categoryName: string, amount: number, icon: string = '') => {
    try {
      await axios.post(`/api/funds/${fundId}/allocations`, { category_name: categoryName, amount, icon });
      if (user.value) {
        const fund = user.value.funds.find((f: any) => f.id === fundId);
        if (fund) {
          fund.allocations.push({ category_name: categoryName, amount, category_icon: icon });
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
      await axios.post('/api/investments', data);
      fetchUser(true);
      return true;
    } catch (err) {
      console.error('Error adding investment', err);
      return false;
    }
  };

  const updateInvestment = async (id: number, payload: any) => {
    try {
      await axios.put(`/api/investments/${id}`, payload);
      fetchUser(true);
      return true;
    } catch (err) {
      console.error('Error updating investment', err);
      return false;
    }
  };

  const deleteInvestment = async (id: number, payload: any = {}) => {
    try {
      await axios.delete(`/api/investments/${id}`, { data: payload });
      fetchUser(true);
      return true;
    } catch (err) {
      console.error('Error deleting investment', err);
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
      isLoading.value = true;
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/user/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.secure_url && user.value) {
        user.value.avatar = response.data.secure_url;
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

  const toggleBalances = () => {
    isBalancesVisible.value = !isBalancesVisible.value;
  };

  const toggleItemVisibility = (id: string) => {
    hiddenBalances.value[id] = !hiddenBalances.value[id];
  };

  const isItemVisible = (id: string) => {
    return isBalancesVisible.value && !hiddenBalances.value[id];
  };

  const freeMoney = computed(() => {
    if (!user.value?.accounts) return 0;
    const accTotal = user.value.accounts.reduce((sum: number, a: any) => sum + parseFloat(a.balance), 0);
    const fundTotal = user.value?.funds ? user.value.funds.reduce((sum: number, f: any) => sum + parseFloat(f.balance), 0) : 0;
    return accTotal - fundTotal;
  });

  const totalFundsAmount = computed(() => {
    if (!user.value?.funds) return 0;
    return user.value.funds.reduce((sum: number, f: any) => sum + parseFloat(f.balance), 0);
  });

  const totalSubscriptionsAmount = computed(() => {
    if (!user.value?.subscriptions) return 0;
    return user.value.subscriptions
      .filter((s: any) => s.status !== 'inactive')
      .reduce((sum: number, s: any) => sum + (s.billing_cycle === 'yearly' ? parseFloat(s.amount) / 12 : parseFloat(s.amount)), 0);
  });
  
  const totalInvestmentsAmount = computed(() => {
    if (liveInvestmentsAmount.value !== null) {
      return liveInvestmentsAmount.value;
    }
    if (!user.value?.investments) return 0;
    return user.value.investments.reduce((sum: number, i: any) => {
      let val = Number(i.quantity || 0) * Number(i.average_price || 1);
      const userCurrency = user.value?.currency || 'MXN';
      if (i.currency === 'USD' && userCurrency === 'MXN') val *= globalExchangeRate.value;
      if (i.currency === 'MXN' && userCurrency === 'USD') val /= globalExchangeRate.value;
      return sum + val;
    }, 0);
  });

  const addFreeMoney = async (amount: number) => {
    try {
      await axios.post('/api/accounts/add-money', { amount });
      if (user.value) {
        // Optimistically update or create Cartera
        if (!user.value.accounts) user.value.accounts = [];
        const cartera = user.value.accounts.find((a: any) => a.name === 'Cartera');
        if (cartera) {
          cartera.balance = (parseFloat(cartera.balance) + amount).toString();
        } else {
          user.value.accounts.push({
            id: Date.now(),
            name: 'Cartera',
            type: 'cash',
            balance: amount.toString()
          });
        }
      }
      return true;
    } catch (err) {
      console.error('Error adding free money', err);
      return false;
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await axios.get('/api/notifications');
      notifications.value = response.data;
    } catch (err) {
      console.error('Error fetching notifications', err);
    }
  };

  return {
    user,
    isLoading,
    error,
    isBalancesVisible,
    notifications,
    toggleBalances,
    toggleItemVisibility,
    isItemVisible,
    fetchUser,
    createFund,
    updateFund,
    allocateFund,
    fetchIncomeStats,
    searchSubscriptionCatalog,
    addSubscription,
    updateProfile,
    uploadAvatar,
    addInvestment,
    updateInvestment,
    deleteInvestment,
    addFreeMoney,
    fetchNotifications,
    freeMoney,
    totalFundsAmount,
    totalSubscriptionsAmount,
    totalInvestmentsAmount
  };
}
