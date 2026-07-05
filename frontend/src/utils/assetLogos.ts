import * as icons from 'simple-icons'

const anyIcons = icons as any;

// Mapeo estricto de símbolos (Tickers) a objetos de simple-icons
const logoMap: Record<string, any> = {
  // Stocks
  'AAPL': anyIcons.siApple,
  'GOOGL': anyIcons.siGoogle,
  'GOOG': anyIcons.siGoogle,
  'META': anyIcons.siMeta,
  'MSFT': anyIcons.siMicrosoft,
  'AMZN': anyIcons.siAmazon,
  'NVDA': anyIcons.siNvidia,
  'NFLX': anyIcons.siNetflix,
  'NETFLIX': anyIcons.siNetflix,
  'TEFLIX': anyIcons.siNetflix, // misspelling

  'TSLA': anyIcons.siTesla,
  'TESLA': anyIcons.siTesla,

  'SPOT': anyIcons.siSpotify,
  'SPOTIFY': anyIcons.siSpotify,
  'SPOTIFFY': anyIcons.siSpotify, // misspelling

  'UBER': anyIcons.siUber,
  'ABNB': anyIcons.siAirbnb,
  'AIRBNB': anyIcons.siAirbnb,

  // Suscripciones Populares
  'CRUNCHYROLL': anyIcons.siCrunchyroll,
  'RUNCHYROLL': anyIcons.siCrunchyroll, // misspelling

  'ICLOUD': anyIcons.siIcloud,
  'ICLOUD+': anyIcons.siIcloud,
  'APPLE': anyIcons.siApple,
  'APPLE MUSIC': anyIcons.siApple,
  'APPLE ONE': anyIcons.siApple,

  'YOUTUBE': anyIcons.siYoutube,
  'YOUTUBE PREMIUM': anyIcons.siYoutube,
  
  'AMAZON': anyIcons.siAmazon,
  'AMAZON PRIME': anyIcons.siAmazon,

  'HBO': anyIcons.siHbo,
  'HBO MAX': anyIcons.siHbomax,
  'MAX': anyIcons.siHbomax,

  'XBOX': anyIcons.siXbox,
  'GAME PASS': anyIcons.siXbox,
  'PLAYSTATION': anyIcons.siPlaystation,
  'PS PLUS': anyIcons.siPlaystation,
  'NINTENDO': anyIcons.siNintendo,

  // Criptomonedas (comúnmente usan estos símbolos o IDs)
  'BTC': anyIcons.siBitcoin,
  'BITCOIN': anyIcons.siBitcoin,
  'ETH': anyIcons.siEthereum,
  'ETHEREUM': anyIcons.siEthereum,
  'SOL': anyIcons.siSolana,
  'SOLANA': anyIcons.siSolana,
  'XRP': anyIcons.siXrp,
  'DOGE': anyIcons.siDogecoin,
  'DOGECOIN': anyIcons.siDogecoin,
  'ADA': anyIcons.siCardano,
  'CARDANO': anyIcons.siCardano,
  'AVAX': anyIcons.siAvalanche,
  'AVALANCHE': anyIcons.siAvalanche,
  'LINK': anyIcons.siChainlink,
  'CHAINLINK': anyIcons.siChainlink,
  'USDT': anyIcons.siTether,
  'TETHER': anyIcons.siTether,
  'BNB': anyIcons.siBinance,
  'BINANCE': anyIcons.siBinance,
}

/**
 * Retorna el objeto de simple-icons correspondiente a un símbolo o nombre,
 * o null si no existe en el diccionario (fallback).
 */
export function getAssetLogo(symbolOrName: string) {
  if (!symbolOrName) return null
  const key = symbolOrName.trim().toUpperCase()
  return logoMap[key] || null
}
