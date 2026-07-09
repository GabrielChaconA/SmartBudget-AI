import axios from 'axios'

const API_KEY = import.meta.env.VITE_API_SPORTS_KEY

const api = axios.create({ baseURL: '' })
// Remove authorization header if any global interceptor adds it
delete api.defaults.headers.common['Authorization']

// Maps OddsApi sport keys to API-Sports proxy endpoints
const SPORT_API_MAP: Record<string, string> = {
  'americanfootball_nfl': '/api-sports-americanfootball',
  'basketball_nba': '/api-sports-basketball',
  'soccer_epl': '/api-sports-football',
  'soccer_uefa_champs_league': '/api-sports-football',
  'soccer_spain_la_liga': '/api-sports-football',
  'soccer_mexico_ligamx': '/api-sports-football',
  'baseball_mlb': '/api-sports-baseball',
  'icehockey_nhl': '/api-sports-hockey',
}

const SPORTMONKS_KEY = import.meta.env.VITE_SPORTMONKS_KEY || import.meta.env.VITE_SPORTMONKS_API_KEY

// Local cache to avoid burning API requests
const logoCache = new Map<string, string | null>()

let isServerCacheLoaded = false
let serverCachePromise: Promise<void> | null = null

async function loadServerCache() {
  if (isServerCacheLoaded) return
  if (serverCachePromise) return serverCachePromise

  serverCachePromise = (async () => {
    try {
      const response = await axios.get('/api/sports/logos')
      const data = response.data
      if (data) {
        Object.keys(data).forEach(key => {
          logoCache.set(key, data[key])
        })
      }
      isServerCacheLoaded = true
    } catch (e) {
      console.error('Error fetching server cache for logos:', e)
    }
  })()

  return serverCachePromise
}

export const apiSportsService = {
  async getSportmonksTeamLogo(teamName: string): Promise<string | null> {
    const key = SPORTMONKS_KEY
    if (!key) return null

    try {
      const queryName = encodeURIComponent(teamName)
      const response = await api.get(`/sportmonks-api/v3/football/teams/search/${queryName}`, {
        params: { api_token: key }
      })
      const results = response.data?.data
      if (results && results.length > 0) {
         return results[0].image_path || null
      }
      return null
    } catch (e) {
      console.error(`Error fetching team logo from Sportmonks for ${teamName}:`, e)
      return null
    }
  },

  async getSportmonksLeagueLogo(leagueName: string): Promise<string | null> {
    const key = SPORTMONKS_KEY
    if (!key) return null

    try {
      const queryName = encodeURIComponent(leagueName)
      const response = await api.get(`/sportmonks-api/v3/football/leagues/search/${queryName}`, {
        params: { api_token: key }
      })
      const results = response.data?.data
      if (results && results.length > 0) {
         return results[0].image_path || null
      }
      return null
    } catch (e) {
      console.error(`Error fetching league logo from Sportmonks for ${leagueName}:`, e)
      return null
    }
  },

  async getTeamLogo(teamName: string, sportKey: string): Promise<string | null> {
    const cacheKey = `${sportKey}_${teamName}`
    
    // Ensure server cache is loaded
    await loadServerCache()

    // Check memory cache first
    if (logoCache.has(cacheKey)) {
      return logoCache.get(cacheKey) || null
    }

    // Check localStorage cache to persist across reloads and save API limits
    const localCacheStr = localStorage.getItem('apiSportsLogos')
    if (localCacheStr) {
       try {
         const localCache = JSON.parse(localCacheStr)
         if (localCache[cacheKey] !== undefined) {
            logoCache.set(cacheKey, localCache[cacheKey])
            return localCache[cacheKey]
         }
       } catch(e) {}
    }

    let logoUrl = null

    if (API_KEY) {
      const baseUrl = SPORT_API_MAP[sportKey]
      if (baseUrl) {
        try {
          const queryName = encodeURIComponent(teamName)
          const response = await api.get(`${baseUrl}/teams`, {
            params: { search: queryName },
            headers: {
              'x-rapidapi-key': API_KEY,
              'x-apisports-key': API_KEY
            }
          })

          const results = response.data.response
          if (results && results.length > 0) {
             const firstMatch = results[0]
             logoUrl = firstMatch.team?.logo || firstMatch.logo || null
          }
        } catch (error) {
          console.error(`Error fetching logo for ${teamName} from API-Sports:`, error)
        }
      }
    }

    // Fallback to Sportmonks if API-Sports didn't find anything
    if (!logoUrl) {
       logoUrl = await this.getSportmonksTeamLogo(teamName)
    }

    logoCache.set(cacheKey, logoUrl)
    
    // Save to localStorage
    const currentCache = JSON.parse(localStorage.getItem('apiSportsLogos') || '{}')
    currentCache[cacheKey] = logoUrl
    localStorage.setItem('apiSportsLogos', JSON.stringify(currentCache))

    // Save to server cache
    axios.post('/api/sports/logos', { key: cacheKey, url: logoUrl }).catch(err => {
       console.error('Error saving logo to server cache:', err)
    })

    return logoUrl
  },

  async getLeagueLogo(leagueName: string, sportKey: string): Promise<string | null> {
    const cacheKey = `league_${sportKey}_${leagueName}`
    
    // Ensure server cache is loaded
    await loadServerCache()

    // Check memory cache first
    if (logoCache.has(cacheKey)) {
      return logoCache.get(cacheKey) || null
    }

    // Check localStorage cache
    const localCacheStr = localStorage.getItem('apiSportsLogos')
    if (localCacheStr) {
       try {
         const localCache = JSON.parse(localCacheStr)
         if (localCache[cacheKey] !== undefined) {
            logoCache.set(cacheKey, localCache[cacheKey])
            return localCache[cacheKey]
         }
       } catch(e) {}
    }

    let logoUrl = null

    if (API_KEY) {
      const baseUrl = SPORT_API_MAP[sportKey]
      if (baseUrl) {
        try {
          const queryName = encodeURIComponent(leagueName)
          const response = await api.get(`${baseUrl}/leagues`, {
            params: { search: queryName },
            headers: {
              'x-rapidapi-key': API_KEY,
              'x-apisports-key': API_KEY
            }
          })

          const results = response.data.response
          if (results && results.length > 0) {
             const firstMatch = results[0]
             logoUrl = firstMatch.league?.logo || firstMatch.logo || null
          }
        } catch (error) {
          console.error(`Error fetching league logo for ${leagueName}:`, error)
        }
      }
    }

    // Fallback to Sportmonks if API-Sports didn't find anything
    if (!logoUrl) {
       logoUrl = await this.getSportmonksLeagueLogo(leagueName)
    }

    logoCache.set(cacheKey, logoUrl)
    
    const currentCache = JSON.parse(localStorage.getItem('apiSportsLogos') || '{}')
    currentCache[cacheKey] = logoUrl
    localStorage.setItem('apiSportsLogos', JSON.stringify(currentCache))

    // Save to server cache
    axios.post('/api/sports/logos', { key: cacheKey, url: logoUrl }).catch(err => {
       console.error('Error saving league logo to server cache:', err)
    })

    return logoUrl
  }
}
