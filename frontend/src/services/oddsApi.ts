import axios from 'axios'

const API_KEY = import.meta.env.VITE_ODDS_API_KEY
const BASE_URL = 'https://api.the-odds-api.com/v4/sports'

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
  async getUpcomingOdds(sport: string = 'upcoming'): Promise<OddsEvent[]> {
    try {
      const response = await axios.get(`${BASE_URL}/${sport}/odds/`, {
        params: {
          apiKey: API_KEY,
          regions: 'us',
          markets: 'h2h',
          oddsFormat: 'decimal'
        }
      })
      // Return top 5 matches
      return response.data.slice(0, 5)
    } catch (error) {
      console.error(`Error fetching Odds API:`, error)
      return []
    }
  }
}
