import axios from 'axios'

const API_KEY = import.meta.env.VITE_ODDS_API_KEY
const BASE_URL = '/odds-api/v4/sports'

const api = axios.create({ baseURL: '' })
delete api.defaults.headers.common['Authorization']

export interface OddsEvent {
  id: string;
  sport_key: string;
  sport_title: string;
  commence_time: string;
  home_team: string;
  away_team: string;
  bookmakers: {
    title: string;
    markets: {
      key: string;
      outcomes: {
        name: string;
        price: number;
      }[];
    }[];
  }[];
}

export const oddsApiService = {
  async getUpcomingOdds(sport: string = 'upcoming', limit: number = 5): Promise<OddsEvent[]> {
    try {
      const response = await api.get(`${BASE_URL}/${sport}/odds/`, {
        params: {
          apiKey: API_KEY,
          regions: 'us',
          markets: 'h2h',
          oddsFormat: 'decimal'
        }
      })
      // Return top limit matches
      return response.data.slice(0, limit)
    } catch (error) {
      // Silently fail if API key is invalid/expired
      return []
    }
  }
}
