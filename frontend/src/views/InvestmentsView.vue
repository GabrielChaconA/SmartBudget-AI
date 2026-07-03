<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { TrendingUp, TrendingDown, Layers, Building2, Bitcoin, Dices, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle, Plus } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { portfolioPerformance, formatCurrency, investmentHoldings, type InvestmentCategory, type InvestmentHolding } from '@/lib/data'
import { finnhubService } from '@/services/finnhub'
import { coingeckoService } from '@/services/coingecko'
import { oddsApiService } from '@/services/oddsApi'
import { useUser } from '@/composables/useUser'
import { useRouter } from 'vue-router'
import AssetLogo from '@/components/AssetLogo.vue'
import AddInvestmentModal from '@/components/AddInvestmentModal.vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const categoryIcons: Record<string, any> = {
  all: Layers,
  etfs: Layers,
  stocks: Building2,
  crypto: Bitcoin,
  bets: Dices,
}

const { user } = useUser()
const router = useRouter()

const isAddModalOpen = ref(false)

const allCategories = [
  { id: 'all', label: 'All Investments', icon: 'all', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'etfs', label: 'ETFs', icon: 'etfs', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'stocks', label: 'Empresas', icon: 'stocks', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'crypto', label: 'Criptos', icon: 'crypto', value: 0, returnPercent: 0, dayPercent: 0 },
  { id: 'bets', label: 'Apuestas', icon: 'bets', value: 0, returnPercent: 0, dayPercent: 0 },
]

const activeCategories = ref<InvestmentCategory[]>(JSON.parse(JSON.stringify(allCategories)))
const activeHoldings = ref<Record<string, InvestmentHolding[]>>({ etfs: [], stocks: [], crypto: [], bets: [] })

const activeCat = ref('all')
const holdings = computed(() => {
  if (activeCat.value === 'all') {
    return [
      ...(activeHoldings.value.etfs || []),
      ...(activeHoldings.value.stocks || []),
      ...(activeHoldings.value.crypto || []),
      ...(activeHoldings.value.bets || [])
    ]
  }
  return activeHoldings.value[activeCat.value] ?? []
})

const totalPortfolioValue = computed(() => {
  return holdings.value.reduce((sum, h) => sum + h.value, 0)
})

const topHoldings = computed(() => {
  const allHoldings = activeCat.value === 'all' 
    ? [
        ...investmentHoldings.etfs,
        ...investmentHoldings.stocks,
        ...investmentHoldings.crypto,
        ...investmentHoldings.bets
      ]
    : investmentHoldings[activeCat.value as keyof typeof investmentHoldings] || [];
    
  return [...allHoldings].sort((a, b) => b.returnPercent - a.returnPercent).slice(0, 5)
})

const isLoading = ref(false)
const isError = ref(false)
const lastUpdate = ref<Date | null>(null)

const getExchangeRate = () => 20.0; // 1 USD = 20 MXN approx

const fetchData = async () => {
  if (!user.value) return;
  isLoading.value = true
  isError.value = false
  
  try {
    const userInvestments = user.value.investments || [];
    
    const etfs = userInvestments.filter((i: any) => i.type === 'etfs');
    const stocks = userInvestments.filter((i: any) => i.type === 'stocks');
    const cryptos = userInvestments.filter((i: any) => i.type === 'crypto');
    const bets = userInvestments.filter((i: any) => i.type === 'bets');
    
    const cryptoIds = cryptos.map((c: any) => c.symbol.toLowerCase())
    
    const [etfRes, stockRes, cryptoRes, oddsRes] = await Promise.allSettled([
      Promise.all(etfs.map((h: any) => finnhubService.getQuote(h.symbol).then(q => ({ h, q })))),
      Promise.all(stocks.map((h: any) => finnhubService.getQuote(h.symbol).then(q => ({ h, q })))),
      cryptoIds.length > 0 ? coingeckoService.getMarkets(cryptoIds) : Promise.resolve([]),
      oddsApiService.getUpcomingOdds()
    ])
    
    const newHoldings: Record<string, InvestmentHolding[]> = { etfs: [], stocks: [], crypto: [], bets: [] }
    
    const processHolding = (h: any, dp: number) => {
      let baseValue = Number(h.quantity);
      if (h.currency === 'USD' && user.value?.currency === 'MXN') {
        baseValue *= getExchangeRate();
      } else if (h.currency === 'MXN' && user.value?.currency === 'USD') {
        baseValue /= getExchangeRate();
      }
      return {
        id: h.id,
        name: h.symbol,
        ticker: h.symbol,
        value: baseValue * (1 + (dp / 100)),
        returnPercent: dp,
        dayPercent: dp
      }
    }

    if (etfRes.status === 'fulfilled') {
      newHoldings.etfs = etfRes.value.map((item: any) => processHolding(item.h, item.q.dp))
    }
    
    if (stockRes.status === 'fulfilled') {
      newHoldings.stocks = stockRes.value.map((item: any) => processHolding(item.h, item.q.dp))
    }
    
    if (cryptoRes.status === 'fulfilled' && cryptoRes.value.length > 0) {
      newHoldings.crypto = cryptos.map((c: any) => {
        const market = cryptoRes.value.find((m: any) => m.symbol.toLowerCase() === c.symbol.toLowerCase())
        return processHolding(c, market ? market.price_change_percentage_24h : 0)
      })
    } else {
      newHoldings.crypto = cryptos.map((c: any) => processHolding(c, 0))
    }
    
    if (oddsRes.status === 'fulfilled' && oddsRes.value.length > 0) {
      newHoldings.bets = bets.map((b: any, index: number) => {
        const event = oddsRes.value[index % oddsRes.value.length];
        const homeOdds = event?.bookmakers?.[0]?.markets?.[0]?.outcomes?.[0]?.price || 1.0;
        const dp = homeOdds > 1.5 ? (homeOdds * 10) : -5;
        return processHolding(b, dp);
      })
    } else {
      newHoldings.bets = bets.map((c: any) => processHolding(c, 0))
    }
    
    activeHoldings.value = newHoldings
    
    activeCategories.value = allCategories.map(cat => {
      let catHoldings = cat.id === 'all' 
        ? Object.values(newHoldings).flat()
        : newHoldings[cat.id] || []
        
      const totalValue = catHoldings.reduce((sum, h) => sum + h.value, 0)
      const avgReturn = catHoldings.length > 0 ? catHoldings.reduce((sum, h) => sum + h.returnPercent, 0) / catHoldings.length : 0;
      
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
  }
}

onMounted(() => {
  fetchData()
})

watch(() => user.value?.investments, () => {
  fetchData()
}, { deep: true })

const chartOption = ref({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => {
      const v = params[0].value
      return `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)}`
    }
  },
  grid: { left: 16, right: 16, top: 16, bottom: 16, containLabel: true },
  xAxis: {
    type: 'category',
    data: portfolioPerformance.map(item => item.month),
    axisLine: { show: false },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: '#333' } },
    axisLabel: {
      formatter: (v: number) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)
    }
  },
  series: [
    {
      data: portfolioPerformance.map(item => item.value),
      type: 'line',
      smooth: true,
      showSymbol: false,
      itemStyle: { color: '#0ea5e9' },
      lineStyle: { width: 3 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{
              offset: 0, color: 'rgba(14, 165, 233, 0.4)'
          }, {
              offset: 1, color: 'rgba(14, 165, 233, 0)'
          }]
        }
      }
    }
  ]
})
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-6xl">
      <header class="pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            Investments
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            Track the performance of your ETFs, companies, crypto and relevant bets.
          </p>
        </div>
        <div class="flex flex-col items-end gap-2">
          <div class="flex items-center gap-3">
            <span v-if="lastUpdate" class="text-xs text-muted-foreground">
              Última actualización: {{ lastUpdate.toLocaleTimeString() }}
            </span>
            <Button variant="outline" size="sm" @click="fetchData" :disabled="isLoading">
              <RefreshCw class="size-4 mr-2" :class="{ 'animate-spin': isLoading }" />
              Actualizar
            </Button>
          </div>
          <span v-if="isError" class="text-xs text-destructive flex items-center gap-1">
            <AlertCircle class="size-3" /> Error al obtener algunos datos
          </span>
        </div>
      </header>

      <!-- Top summary -->
      <div class="grid gap-4 lg:grid-cols-3">
        <Card class="lg:col-span-2 border-border">
          <CardHeader class="flex-row items-start justify-between space-y-0">
            <div>
              <CardDescription>{{ activeCat === 'all' ? 'Total portfolio value' : activeCategories.find(c => c.id === activeCat)?.label + ' Value' }}</CardDescription>
              <CardTitle class="text-3xl">
                {{ formatCurrency(totalPortfolioValue, user?.currency || 'MXN') }}
              </CardTitle>
              <div class="mt-2 flex items-center gap-3">
                <span :class="[
                  'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                  (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) >= 0 ? 'text-primary' : 'text-destructive'
                ]">
                  <ArrowUpRight v-if="(activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) >= 0" class="size-3.5" />
                  <ArrowDownRight v-else class="size-3.5" />
                  {{ (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) > 0 ? '+' : '' }}{{ (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0).toFixed(1) }}%
                </span>
                <span class="text-sm text-muted-foreground">today</span>
              </div>
            </div>
            <span class="flex size-11 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <TrendingUp class="size-5" />
            </span>
          </CardHeader>
          <CardContent>
            <div class="h-[200px] w-full">
              <v-chart class="h-full w-full" :option="chartOption" autoresize />
            </div>
          </CardContent>
        </Card>

        <Card class="border-border cursor-pointer hover:border-primary/50 transition-colors group" @click="isAddModalOpen = true">
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle class="text-base">Summary</CardTitle>
              <div class="flex size-6 items-center justify-center rounded bg-primary text-primary-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                <Plus class="size-4" />
              </div>
            </div>
            <CardDescription>Capital and gains. Click to add.</CardDescription>
          </CardHeader>
          <CardContent class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Invested</span>
              <span class="font-semibold tabular-nums text-foreground">
                {{ formatCurrency(totalPortfolioValue, user?.currency || 'MXN') }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Current value</span>
              <span class="font-semibold tabular-nums text-foreground">
                {{ formatCurrency(totalPortfolioValue, user?.currency || 'MXN') }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Total gain</span>
              <span class="font-semibold tabular-nums text-primary">
                {{ formatCurrency(0, user?.currency || 'MXN') }}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Category cards -->
      <section class="mt-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          By category
        </h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <button
            v-for="cat in activeCategories"
            :key="cat.id"
            type="button"
            @click="activeCat = cat.id"
            :class="[
              'rounded-xl border p-4 text-left transition-colors',
              activeCat === cat.id ? 'border-primary bg-accent' : 'border-border bg-card hover:border-primary/50'
            ]"
          >
            <div class="flex items-center justify-between">
              <span :class="[
                'flex size-10 items-center justify-center rounded-xl',
                activeCat === cat.id ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'
              ]">
                <component :is="categoryIcons[cat.id]" class="size-5" />
              </span>
              <span :class="[
                'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                cat.returnPercent >= 0 ? 'text-primary' : 'text-destructive'
              ]">
                <ArrowUpRight v-if="cat.returnPercent >= 0" class="size-3.5" />
                <ArrowDownRight v-else class="size-3.5" />
                {{ cat.returnPercent > 0 ? '+' : '' }}{{ cat.returnPercent.toFixed(1) }}%
              </span>
            </div>
            <p class="mt-3 text-sm text-muted-foreground">{{ cat.label }}</p>
            <p class="text-lg font-semibold text-foreground">
              {{ formatCurrency(cat.value, user?.currency || 'MXN') }}
            </p>
          </button>
        </div>
      </section>

      <!-- Holdings for active category -->
      <section class="mt-8">
        <div class="mb-3 flex items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            {{ activeCategories.find(c => c.id === activeCat)?.label }} Top Movers
          </h2>
          <Badge variant="secondary">{{ topHoldings.length }}</Badge>
        </div>
        <Card class="border-border" v-if="topHoldings.length > 0">
          <CardContent class="divide-y divide-border p-0">
            <div
              v-for="h in topHoldings"
              :key="h.id"
              class="flex items-center gap-4 px-4 py-4 sm:px-6"
            >
              <span :class="[
                'flex size-10 items-center justify-center rounded-xl text-sm font-semibold overflow-hidden',
                h.returnPercent >= 0 ? 'bg-primary/15 text-primary' : 'bg-destructive/15 text-destructive'
              ]">
                <AssetLogo :symbol="h.ticker" :fallback-icon="h.returnPercent >= 0 ? TrendingUp : TrendingDown" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-foreground">
                  {{ h.name }}
                </p>
                <p class="text-sm text-muted-foreground">{{ h.ticker }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-foreground tabular-nums">
                  {{ formatCurrency(h.value, user?.currency || 'MXN') }}
                </p>
                <div class="flex items-center justify-end gap-2">
                  <span :class="[
                    'inline-flex items-center gap-0.5 text-xs font-medium tabular-nums',
                    h.returnPercent >= 0 ? 'text-primary' : 'text-destructive'
                  ]">
                    <ArrowUpRight v-if="h.returnPercent >= 0" class="size-3.5" />
                    <ArrowDownRight v-else class="size-3.5" />
                    {{ h.returnPercent > 0 ? '+' : '' }}{{ h.returnPercent.toFixed(1) }}%
                  </span>
                  <span class="text-xs text-muted-foreground">today</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card v-else class="border-border border-dashed p-8 text-center text-muted-foreground">
          No top movers found for this category at the moment.
        </Card>
        
        <div class="mt-6 flex justify-center">
          <Button variant="outline" class="w-full sm:w-auto" @click="router.push(`/market-gainers?category=${activeCat}`)">
            See more market options
          </Button>
        </div>
      </section>
    </div>
    
    <AddInvestmentModal v-model:open="isAddModalOpen" />
  </DashboardLayout>
</template>
