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

export interface SportConfig {
  key: string;
  title: string;
  description: string;
}

export const TOP_SPORTS: SportConfig[] = [
  { key: 'americanfootball_nfl', title: 'NFL', description: 'US Football' },
  { key: 'basketball_nba', title: 'NBA', description: 'US Basketball' },
  { key: 'soccer_epl', title: 'Premier League', description: 'English Soccer' },
  { key: 'soccer_uefa_champs_league', title: 'Champions League', description: 'European Soccer' },
  { key: 'soccer_spain_la_liga', title: 'La Liga', description: 'Spanish Soccer' },
  { key: 'baseball_mlb', title: 'MLB', description: 'US Baseball' },
  { key: 'icehockey_nhl', title: 'NHL', description: 'US Hockey' },
  { key: 'mma_mixed_martial_arts', title: 'MMA', description: 'Mixed Martial Arts' },
  { key: 'tennis_atp_wimbledon', title: 'Wimbledon', description: 'ATP Tennis' },
  { key: 'soccer_mexico_ligamx', title: 'Liga MX', description: 'Mexican Soccer' }
]

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
