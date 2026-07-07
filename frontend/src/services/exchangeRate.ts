import axios from 'axios'

// Uses open.er-api.com - free, no API key required, updated daily
const BASE_URL = 'https://open.er-api.com/v6/latest'

// In-memory cache to avoid hammering the API on every component mount
let cachedRate: number | null = null
let cacheTimestamp: number | null = null
const CACHE_TTL_MS = 10 * 60 * 1000 // 10 minutes

const api = axios.create()
delete api.defaults.headers.common['Authorization']

export const exchangeRateService = {
  async getUsdMxnRate(): Promise<number> {
    const now = Date.now()
    if (cachedRate !== null && cacheTimestamp !== null && (now - cacheTimestamp) < CACHE_TTL_MS) {
      return cachedRate
    }
    try {
      const response = await api.get(`${BASE_URL}/USD`)
      const rate = response.data?.rates?.MXN
      if (rate && typeof rate === 'number' && rate > 1) {
        cachedRate = rate
        cacheTimestamp = now
        return rate
      }
    } catch (e) {
      console.warn('[exchangeRateService] Failed to fetch rate, using fallback', e)
    }
    return cachedRate ?? 17.5
  }
}
