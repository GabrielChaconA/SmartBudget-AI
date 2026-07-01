import axios from 'axios'

const BASE_URL = 'https://api.coingecko.com/api/v3'

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
      const response = await axios.get(`${BASE_URL}/coins/markets`, {
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
  }
}
