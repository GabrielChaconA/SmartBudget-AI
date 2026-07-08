import axios from 'axios'

const API_KEY = import.meta.env.VITE_FMP_API_KEY
const BASE_URL = '/fmp-api/api/v3'

const api = axios.create({ baseURL: '' })
delete api.defaults.headers.common['Authorization']

export interface FMPProfile {
  symbol: string;
  companyName: string;
  mktCap: number;
  image: string;
  exchangeShortName: string;
}

export interface FMPGainer {
  symbol: string;
  name: string;
  change: number;
  price: number;
  changesPercentage: number;
}

import { finnhubService } from './finnhub'

export const fmpService = {
  async getProfile(symbol: string): Promise<FMPProfile | null> {
    try {
      const response = await api.get(`${BASE_URL}/profile/${symbol}`, {
        params: {
          apikey: API_KEY
        }
      })
      if (response.data && response.data.length > 0) {
        return response.data[0]
      }
      return null
    } catch (error) {
      console.error(`Error fetching FMP profile for ${symbol}:`, error)
      return null
    }
  },
  async getMarketMovers(type: 'gainers' | 'losers' = 'gainers'): Promise<FMPGainer[]> {
    // FMP API is blocking free keys for the gainers endpoint (403 Forbidden). 
    // Fallback: Fetch a list of popular stocks from Finnhub to simulate gainers/losers.
    // Reduced to 10 to avoid hitting Finnhub's 60 req/min free limit too fast.
    const popularTickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'AMD', 'NFLX', 'SPOT']
    try {
      const quotes = await Promise.all(
        popularTickers.map(t => finnhubService.getQuote(t).then(q => ({ symbol: t, q })).catch(() => null))
      )
      const valid = quotes.filter(q => q !== null) as { symbol: string, q: any }[]
      
      const movers = valid.map(item => ({
        symbol: item.symbol,
        name: item.symbol, // Using symbol as name since Finnhub quote doesn't include company name
        change: item.q.d,
        price: item.q.c,
        changesPercentage: item.q.dp
      }))
      
      if (type === 'gainers') {
        return movers.sort((a, b) => b.changesPercentage - a.changesPercentage)
      } else {
        return movers.sort((a, b) => a.changesPercentage - b.changesPercentage)
      }
    } catch (error) {
      console.error(`Error fetching FMP market movers via fallback:`, error)
      return []
    }
  }
}
