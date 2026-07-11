import { ref, computed, watch } from 'vue'
import { finnhubService } from '@/services/finnhub'
import { coingeckoService } from '@/services/coingecko'
import { binanceService } from '@/services/binance'
import { exchangeRateService } from '@/services/exchangeRate'
import { oddsApiService } from '@/services/oddsApi'
import type { InvestmentCategory, InvestmentHolding } from '@/lib/data'
import { useUser } from '@/composables/useUser'

// Module-level singleton state shared across all components
const allCategories: InvestmentCategory[] = [
  { id: 'all', label: 'All Investments', icon: 'all', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'etfs', label: 'ETFs', icon: 'etfs', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'stocks', label: 'Empresas', icon: 'stocks', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'crypto', label: 'Criptos', icon: 'crypto', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'bets', label: 'Apuestas', icon: 'bets', value: 0, returnPercent: 0, dayPercent: 0 },
]

const activeCategories = ref<InvestmentCategory[]>(JSON.parse(JSON.stringify(allCategories)))
const activeHoldings = ref<Record<string, InvestmentHolding[]>>({ etfs: [], stocks: [], crypto: [], bets: [] })

const isLoading = ref(false)
const isError = ref(false)
const lastUpdate = ref<Date | null>(null)
const exchangeRate = ref(20.0)

const allHoldings = computed(() => [
  ...(activeHoldings.value.etfs || []),
  ...(activeHoldings.value.stocks || []),
  ...(activeHoldings.value.crypto || []),
  ...(activeHoldings.value.bets || [])
])

const totalPortfolioValue = computed(() => allHoldings.value.reduce((sum, h) => sum + h.value, 0))

let fetchPromise: Promise<void> | null = null

const fetchData = async (user: any) => {
  if (!user) return
  // Deduplicate concurrent calls
  if (fetchPromise) return fetchPromise

  fetchPromise = (async () => {
    isLoading.value = true
    isError.value = false

    try {
      const userInvestments = user.investments || []

      const etfs = userInvestments.filter((i: any) => i.type === 'etfs')
      const stocks = userInvestments.filter((i: any) => i.type === 'stocks')
      const cryptos = userInvestments.filter((i: any) => i.type === 'crypto')
      const bets = userInvestments.filter((i: any) => i.type === 'bets')

      const cryptoMap: Record<string, string> = {
        'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana', 'xrp': 'ripple',
        'ada': 'cardano', 'doge': 'dogecoin', 'dot': 'polkadot', 'matic': 'matic-network',
        'usdt': 'tether', 'usdc': 'usd-coin'
      }
      const cryptoIds = cryptos.map((c: any) => {
        const sym = c.symbol.toLowerCase()
        return cryptoMap[sym] || sym
      })

      const fetchQuoteSafe = async (h: any) => {
        try {
          const q = await finnhubService.getQuote(h.symbol)
          return { h, q }
        } catch {
          return { h, q: { c: h.average_price || 0, dp: 0, d: 0, h: 0, l: 0, o: 0, pc: 0 } }
        }
      }

      const [etfRes, stockRes, cryptoRes, oddsRes, usdRes] = await Promise.allSettled([
        Promise.all(etfs.map(fetchQuoteSafe)),
        Promise.all(stocks.map(fetchQuoteSafe)),
        cryptoIds.length > 0
          ? binanceService.getMarkets(cryptoIds).catch(() => coingeckoService.getMarkets(cryptoIds).catch(() => []))
          : Promise.resolve([]),
        oddsApiService.getUpcomingOdds(),
        exchangeRateService.getUsdMxnRate()
      ])

      if (usdRes.status === 'fulfilled') {
        exchangeRate.value = usdRes.value
      }

      const newHoldings: Record<string, InvestmentHolding[]> = { etfs: [], stocks: [], crypto: [], bets: [] }

      const processHolding = (h: any, dp: number, currentPriceUsd?: number) => {
        let currentPriceNative = h.average_price || 1
        if (currentPriceUsd !== undefined) {
          currentPriceNative = currentPriceUsd * (h.currency === 'MXN' ? exchangeRate.value : 1)
        } else {
          currentPriceNative = (h.average_price || 1) * (1 + (dp / 100))
        }

        const originalValueNative = h.quantity * (h.average_price || 1)
        const currentValueNative = h.quantity * currentPriceNative

        const historicalReturn = (h.average_price && h.average_price > 0)
          ? ((currentPriceNative - h.average_price) / h.average_price) * 100
          : 0

        let currentValueBase = currentValueNative
        const userCurrency = user.currency || 'MXN'
        if (h.currency === 'USD' && userCurrency === 'MXN') {
          currentValueBase *= exchangeRate.value
        } else if (h.currency === 'MXN' && userCurrency === 'USD') {
          currentValueBase /= exchangeRate.value
        }

        return {
          id: h.id,
          name: h.symbol,
          ticker: h.symbol,
          value: currentValueBase,
          originalValue: currentValueNative,
          originalCurrency: h.currency || 'MXN',
          created_at: h.created_at,
          returnPercent: historicalReturn,
          dayPercent: dp,
          totalInvestedNative: originalValueNative
        }
      }

      if (etfRes.status === 'fulfilled') {
        newHoldings.etfs = etfRes.value.map((item: any) => processHolding(item.h, item.q.dp, item.q.c))
      }

      if (stockRes.status === 'fulfilled') {
        newHoldings.stocks = stockRes.value.map((item: any) => processHolding(item.h, item.q.dp, item.q.c))
      }

      if (cryptoRes.status === 'fulfilled' && cryptoRes.value.length > 0) {
        newHoldings.crypto = cryptos.map((h: any) => {
          const sym = h.symbol.toLowerCase()
          const coinId = cryptoMap[sym] || sym
          const market = cryptoRes.value.find((m: any) => m.id === coinId || m.symbol?.toLowerCase() === sym)
          if (market) {
            const priceUsd = market.current_price
            const userCurrency = user.currency || 'MXN'
            const currentValueUsd = h.quantity * priceUsd
            const currentValueInUserCurrency = userCurrency === 'MXN'
              ? currentValueUsd * (exchangeRate.value || 20)
              : currentValueUsd
              const historicalReturn = (h.average_price && h.average_price > 0)
                ? ((priceUsd - h.average_price) / h.average_price) * 100
                : 0;

            const originalValueNative = h.quantity * (h.average_price || priceUsd);
            const currentValueNative = h.quantity * priceUsd;

            return {
              id: h.id,
              name: h.symbol,
              ticker: h.symbol,
              value: currentValueInUserCurrency,
              originalValue: currentValueUsd, // We keep the USD original value for reference
              originalCurrency: 'USD',
              created_at: h.created_at,
              returnPercent: historicalReturn,
              dayPercent: market.price_change_percentage_24h || 0,
              totalInvestedNative: originalValueNative // Important for calculating the actual return amount correctly
            }
          }
          return processHolding(h, 0)
        })
      } else {
        newHoldings.crypto = cryptos.map((c: any) => processHolding(c, 0))
      }

      if (oddsRes.status === 'fulfilled' && oddsRes.value.length > 0) {
        newHoldings.bets = bets.map((b: any, index: number) => {
          const event = oddsRes.value[index % oddsRes.value.length]
          const homeOdds = event?.bookmakers?.[0]?.markets?.[0]?.outcomes?.[0]?.price || 1.0
          const dp = homeOdds > 1.5 ? (homeOdds * 10) : -5
          return processHolding(b, dp)
        })
      } else {
        newHoldings.bets = bets.map((c: any) => processHolding(c, 0))
      }

      activeHoldings.value = newHoldings

      activeCategories.value = allCategories.map(cat => {
        const catHoldings = cat.id === 'all'
          ? Object.values(newHoldings).flat()
          : newHoldings[cat.id] || []

        const totalValue = catHoldings.reduce((sum, h) => sum + h.value, 0)
        const totalInvested = catHoldings.reduce((sum, h) => sum + h.originalValue, 0)
        
        let avgReturn = 0;
        if (totalInvested > 0) {
          avgReturn = ((totalValue - totalInvested) / totalInvested) * 100;
        }

        return {
          ...cat,
          value: totalValue,
          returnPercent: avgReturn,
          dayPercent: avgReturn
        }
      })
    } catch (e) {
      console.error(e)
      isError.value = true
    } finally {
      isLoading.value = false
      lastUpdate.value = new Date()
      fetchPromise = null
    }
  })()

  return fetchPromise
}

let isWatcherSetup = false

export function useInvestments() {
  if (!isWatcherSetup) {
    const { user } = useUser()
    watch(() => user.value?.investments, (newInvestments) => {
      if (user.value) {
        fetchData(user.value)
      }
    }, { deep: true, immediate: true })
    isWatcherSetup = true
  }

  return {
    allCategories,
    activeCategories,
    activeHoldings,
    allHoldings,
    totalPortfolioValue,
    isLoading,
    isError,
    lastUpdate,
    exchangeRate,
    fetchData
  }
}
