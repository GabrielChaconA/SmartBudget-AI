import axios from 'axios'

const API_KEY = import.meta.env.VITE_BINANCE_API_KEY
const BASE_URL = 'https://api.binance.com/api/v3'

const api = axios.create()
// Do not attach X-MBX-APIKEY for public endpoints to avoid CORS preflight failures
delete api.defaults.headers.common['Authorization']

export interface BinanceTicker {
  symbol: string;
  priceChangePercent: string;
  lastPrice: string;
}

const coingeckoToBinanceMap: Record<string, string> = {
  'bitcoin': 'BTCUSDT',
  'ethereum': 'ETHUSDT',
  'solana': 'SOLUSDT',
  'ripple': 'XRPUSDT',
  'cardano': 'ADAUSDT',
  'dogecoin': 'DOGEUSDT',
  'polkadot': 'DOTUSDT',
  'matic-network': 'MATICUSDT',
  'tether': 'USDTUSDT',
  'usd-coin': 'USDCUSDT'
}

const binanceToCoingeckoMap = Object.entries(coingeckoToBinanceMap).reduce((acc, [key, value]) => {
  acc[value] = key;
  return acc;
}, {} as Record<string, string>);

export const binanceService = {
  async getMarkets(coingeckoIds: string[]): Promise<any[]> {
    try {
      const symbols = coingeckoIds.map(id => coingeckoToBinanceMap[id] || `${id.toUpperCase()}USDT`);
      if (symbols.length === 0) return [];
      
      const response = await api.get(`${BASE_URL}/ticker/24hr`);
      
      const allTickers: BinanceTicker[] = Array.isArray(response.data) ? response.data : [response.data];
      
      const data = allTickers.filter(ticker => symbols.includes(ticker.symbol));
      
      return data.map(ticker => {
        const coingeckoId = binanceToCoingeckoMap[ticker.symbol];
        return {
          id: coingeckoId || ticker.symbol.replace('USDT', '').toLowerCase(),
          symbol: ticker.symbol.replace('USDT', '').toLowerCase(),
          name: ticker.symbol.replace('USDT', ''),
          current_price: parseFloat(ticker.lastPrice),
          price_change_percentage_24h: parseFloat(ticker.priceChangePercent)
        };
      });
    } catch (error) {
      console.error(`Error fetching Binance markets:`, error);
      throw error;
    }
  },
  
  async getMarketMovers(type: 'gainers' | 'losers' = 'gainers'): Promise<any[]> {
    try {
      const response = await api.get(`${BASE_URL}/ticker/24hr`);
      const data: BinanceTicker[] = response.data;
      
      const usdtPairs = data.filter(t => t.symbol.endsWith('USDT') && parseFloat(t.lastPrice) > 0.001);
      
      if (type === 'gainers') {
        usdtPairs.sort((a, b) => parseFloat(b.priceChangePercent) - parseFloat(a.priceChangePercent));
      } else {
        usdtPairs.sort((a, b) => parseFloat(a.priceChangePercent) - parseFloat(b.priceChangePercent));
      }
      
      const top = usdtPairs.slice(0, 20);
      
      return top.map(ticker => {
        const coingeckoId = binanceToCoingeckoMap[ticker.symbol];
        return {
          id: coingeckoId || ticker.symbol.replace('USDT', '').toLowerCase(),
          symbol: ticker.symbol.replace('USDT', '').toLowerCase(),
          name: ticker.symbol.replace('USDT', ''),
          current_price: parseFloat(ticker.lastPrice),
          price_change_percentage_24h: parseFloat(ticker.priceChangePercent)
        };
      });
    } catch (error) {
      console.error(`Error fetching Binance market movers:`, error);
      throw error;
    }
  },

  subscribeToTickers(coingeckoIds: string[], callback: (coingeckoId: string, price: number, change: number) => void): () => void {
    const symbols = coingeckoIds.map(id => coingeckoToBinanceMap[id] || `${id.toUpperCase()}USDT`).filter(Boolean);
    if (symbols.length === 0) return () => {};

    const streams = symbols.map(s => `${s.toLowerCase()}@ticker`).join('/');
    const wsUrl = `wss://stream.binance.com:9443/stream?streams=${streams}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload && payload.data && payload.data.c) {
          const ticker = payload.data;
          const coingeckoId = binanceToCoingeckoMap[ticker.s] || ticker.s.replace('USDT', '').toLowerCase();
          callback(coingeckoId, parseFloat(ticker.c), parseFloat(ticker.P)); // c = last price, P = price change percent
        }
      } catch (e) {
        console.error('Error parsing Binance WS message', e);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }
}
