import axios from 'axios'

const API_KEY = import.meta.env.VITE_FINNHUB_API_KEY
const BASE_URL = 'https://finnhub.io/api/v1'

const api = axios.create()
delete api.defaults.headers.common['Authorization']

export interface FinnhubQuote {
  c: number; // Current price
  d: number; // Change
  dp: number; // Percent change
  h: number; // High
  l: number; // Low
  o: number; // Open
  pc: number; // Previous close
}

const cache = new Map<string, { data: FinnhubQuote, timestamp: number }>()
const CACHE_DURATION_MS = 60000 // 1 minute

export const finnhubService = {
  async getQuote(symbol: string): Promise<FinnhubQuote> {
    const cached = cache.get(symbol)
    if (cached && (Date.now() - cached.timestamp < CACHE_DURATION_MS)) {
      return cached.data
    }

    try {
      const response = await api.get(`${BASE_URL}/quote`, {
        params: {
          symbol,
          token: API_KEY
        }
      })
      cache.set(symbol, { data: response.data, timestamp: Date.now() })
      return response.data
    } catch (error) {
      throw error
    }
  },

  subscribeToTickers(symbols: string[], callback: (symbol: string, price: number) => void): () => void {
    if (symbols.length === 0) return () => {};
    
    const ws = new WebSocket(`wss://ws.finnhub.io?token=${API_KEY}`);
    
    ws.onopen = () => {
      symbols.forEach(symbol => {
        ws.send(JSON.stringify({ 'type': 'subscribe', 'symbol': symbol }));
      });
    };
    
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'trade' && payload.data) {
          // payload.data is an array of trades. Find the latest trade for each symbol
          const latestTrades = new Map<string, number>();
          payload.data.forEach((trade: any) => {
            latestTrades.set(trade.s, trade.p); // s = symbol, p = price
          });
          
          latestTrades.forEach((price, symbol) => {
            callback(symbol, price);
          });
        }
      } catch (e) {
        console.error('Error parsing Finnhub WS message', e);
      }
    };
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        symbols.forEach(symbol => {
          ws.send(JSON.stringify({ 'type': 'unsubscribe', 'symbol': symbol }));
        });
        ws.close();
      }
    };
  }
}
