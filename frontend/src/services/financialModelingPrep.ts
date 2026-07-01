import axios from 'axios'

const API_KEY = import.meta.env.VITE_FMP_API_KEY
const BASE_URL = 'https://financialmodelingprep.com/api/v3'

export interface FMPProfile {
  symbol: string;
  companyName: string;
  mktCap: number;
  image: string;
  exchangeShortName: string;
}

export const fmpService = {
  async getProfile(symbol: string): Promise<FMPProfile | null> {
    try {
      const response = await axios.get(`${BASE_URL}/profile/${symbol}`, {
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
  }
}
