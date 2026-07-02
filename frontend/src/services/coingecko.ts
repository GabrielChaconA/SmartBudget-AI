import axios from 'axios'

const BASE_URL = 'https://api.coingecko.com/api/v3'

const api = axios.create()
delete api.defaults.headers.common['Authorization']

export interface CoinGeckoMarket {
  id: string;
  symbol: string;
  name: string;
  image: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  total_volume: number;
  price_change_percentage_24h: number;
}

export const coingeckoService = {
  async getMarkets(ids: string[]): Promise<CoinGeckoMarket[]> {
    try {
      const response = await api.get(`${BASE_URL}/coins/markets`, {
        params: {
          vs_currency: 'usd',
          ids: ids.join(',')
        }
      })
      return response.data
    } catch (error) {
      console.error(`Error fetching CoinGecko markets:`, error)
      return []
    }
  },
  async getMarketMovers(type: 'gainers' | 'losers' = 'gainers'): Promise<CoinGeckoMarket[]> {
    try {
      const response = await api.get(`${BASE_URL}/coins/markets`, {
        params: {
          vs_currency: 'usd',
          order: 'market_cap_desc',
          per_page: 100,
          page: 1
        }
      })
      const markets: CoinGeckoMarket[] = response.data || []
      const withChanges = markets.filter(m => m.price_change_percentage_24h !== null)
      
      if (type === 'gainers') {
        return withChanges.sort((a, b) => b.price_change_percentage_24h - a.price_change_percentage_24h).slice(0, 20)
      } else {
        return withChanges.sort((a, b) => a.price_change_percentage_24h - b.price_change_percentage_24h).slice(0, 20)
      }
    } catch (error) {
      console.error(`Error fetching CoinGecko market movers:`, error)
      return []
    }
  }
}
