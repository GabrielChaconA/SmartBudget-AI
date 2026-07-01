import axios from 'axios'

const API_KEY = import.meta.env.VITE_FINNHUB_API_KEY
const BASE_URL = 'https://finnhub.io/api/v1'

export interface FinnhubQuote {
  c: number; // Current price
  d: number; // Change
  dp: number; // Percent change
  h: number; // High
  l: number; // Low
  o: number; // Open
  pc: number; // Previous close
}

export const finnhubService = {
  async getQuote(symbol: string): Promise<FinnhubQuote> {
    const response = await axios.get(`${BASE_URL}/quote`, {
      params: {
        symbol,
        token: API_KEY
      }
    })
    return response.data
  }
}
