import * as icons from 'simple-icons'

// Mapeo estricto de símbolos (Tickers) a objetos de simple-icons
const logoMap: Record<string, any> = {
  // Stocks
  'AAPL': icons.siApple,
  'GOOGL': icons.siGoogle,
  'GOOG': icons.siGoogle,
  'META': icons.siMeta,
  'MSFT': icons.siMicrosoft,
  'AMZN': icons.siAmazon,
  'NVDA': icons.siNvidia,
  'NFLX': icons.siNetflix,
  'NETFLIX': icons.siNetflix,
  'TEFLIX': icons.siNetflix, // misspelling

  'TSLA': icons.siTesla,
  'TESLA': icons.siTesla,

  'SPOT': icons.siSpotify,
  'SPOTIFY': icons.siSpotify,
  'SPOTIFFY': icons.siSpotify, // misspelling

  'UBER': icons.siUber,
  'ABNB': icons.siAirbnb,
  'AIRBNB': icons.siAirbnb,

  // Suscripciones Populares
  'CRUNCHYROLL': icons.siCrunchyroll,
  'RUNCHYROLL': icons.siCrunchyroll, // misspelling

  'ICLOUD': icons.siIcloud,
  'ICLOUD+': icons.siIcloud,
  'APPLE': icons.siApple,
  'APPLE MUSIC': icons.siApple,
  'APPLE ONE': icons.siApple,

  'YOUTUBE': icons.siYoutube,
  'YOUTUBE PREMIUM': icons.siYoutube,
  
  'AMAZON': icons.siAmazon,
  'AMAZON PRIME': icons.siAmazon,

  'HBO': icons.siHbo,
  'HBO MAX': icons.siHbomax,
  'MAX': icons.siHbomax,

  'XBOX': icons.siXbox,
  'GAME PASS': icons.siXbox,
  'PLAYSTATION': icons.siPlaystation,
  'PS PLUS': icons.siPlaystation,
  'NINTENDO': icons.siNintendo,

  // Criptomonedas (comúnmente usan estos símbolos o IDs)
  'BTC': icons.siBitcoin,
  'BITCOIN': icons.siBitcoin,
  'ETH': icons.siEthereum,
  'ETHEREUM': icons.siEthereum,
  'SOL': icons.siSolana,
  'SOLANA': icons.siSolana,
  'XRP': icons.siXrp,
  'DOGE': icons.siDogecoin,
  'DOGECOIN': icons.siDogecoin,
  'ADA': icons.siCardano,
  'CARDANO': icons.siCardano,
  'AVAX': icons.siAvalanche,
  'AVALANCHE': icons.siAvalanche,
  'LINK': icons.siChainlink,
  'CHAINLINK': icons.siChainlink,
  'USDT': icons.siTether,
  'TETHER': icons.siTether,
  'BNB': icons.siBinance,
  'BINANCE': icons.siBinance,
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
