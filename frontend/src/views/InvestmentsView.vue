<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { TrendingUp, TrendingDown, Layers, Building2, Bitcoin, Dices, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { investmentsSummary, portfolioPerformance, investmentCategories as fallbackCategories, investmentHoldings as fallbackHoldings, formatCurrency, type InvestmentCategory, type InvestmentHolding } from '@/lib/data'
import { finnhubService } from '@/services/finnhub'
import { coingeckoService } from '@/services/coingecko'
import { oddsApiService } from '@/services/oddsApi'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const categoryIcons: Record<string, any> = {
  etf: Layers,
  company: Building2,
  crypto: Bitcoin,
  bet: Dices,
}

const activeCategories = ref<InvestmentCategory[]>([...fallbackCategories])
const activeHoldings = ref<Record<string, InvestmentHolding[]>>({ ...fallbackHoldings })

const activeCat = ref(activeCategories.value[0].id)
const holdings = computed(() => activeHoldings.value[activeCat.value] ?? [])

const isLoading = ref(false)
const isError = ref(false)
const lastUpdate = ref<Date | null>(null)

const fetchData = async () => {
  isLoading.value = true
  isError.value = false
  
  try {
    const cryptoIds = fallbackHoldings.crypto.map(c => c.name.toLowerCase())
    
    const [etfRes, stockRes, cryptoRes, oddsRes] = await Promise.allSettled([
      Promise.all(fallbackHoldings.etfs.map(h => finnhubService.getQuote(h.ticker).then(q => ({ h, q })))),
      Promise.all(fallbackHoldings.stocks.map(h => finnhubService.getQuote(h.ticker).then(q => ({ h, q })))),
      coingeckoService.getMarkets(cryptoIds),
      oddsApiService.getUpcomingOdds()
    ])
    
    const newHoldings = { ...fallbackHoldings }
    
    if (etfRes.status === 'fulfilled') {
      newHoldings.etfs = etfRes.value.map(item => ({
        ...item.h,
        value: item.q.c > 0 ? item.q.c * (item.h.value / 100) : item.h.value,
        returnPercent: item.q.dp,
        dayPercent: item.q.dp
      }))
    }
    
    if (stockRes.status === 'fulfilled') {
      newHoldings.stocks = stockRes.value.map(item => ({
        ...item.h,
        value: item.q.c > 0 ? item.q.c * (item.h.value / 100) : item.h.value,
        returnPercent: item.q.dp,
        dayPercent: item.q.dp
      }))
    }
    
    if (cryptoRes.status === 'fulfilled' && cryptoRes.value.length > 0) {
      newHoldings.crypto = newHoldings.crypto.map(c => {
        const market = cryptoRes.value.find(m => m.symbol.toLowerCase() === c.ticker.toLowerCase())
        if (market) {
          return {
            ...c,
            name: market.name,
            value: market.current_price * (c.value / 1000),
            returnPercent: market.price_change_percentage_24h,
            dayPercent: market.price_change_percentage_24h
          }
        }
        return c
      })
    }
    
    if (oddsRes.status === 'fulfilled' && oddsRes.value.length > 0) {
      newHoldings.bets = oddsRes.value.slice(0, 3).map((event, index) => {
        const fallback = fallbackHoldings.bets[index] || fallbackHoldings.bets[0]
        const homeOdds = event.bookmakers?.[0]?.markets?.[0]?.outcomes?.[0]?.price || 1.0
        return {
          id: event.id,
          name: `${event.home_team} vs ${event.away_team}`,
          ticker: event.sport_title,
          value: fallback.value,
          returnPercent: homeOdds,
          dayPercent: 0
        }
      })
    }
    
    activeHoldings.value = newHoldings
    
    activeCategories.value = activeCategories.value.map(cat => {
      const catHoldings = newHoldings[cat.id as keyof typeof newHoldings] || []
      const totalValue = catHoldings.reduce((sum, h) => sum + h.value, 0)
      return {
        ...cat,
        value: totalValue > 0 ? totalValue : cat.value
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
              <CardDescription>Total portfolio value</CardDescription>
              <CardTitle class="text-3xl">
                {{ formatCurrency(investmentsSummary.totalValue) }}
              </CardTitle>
              <div class="mt-2 flex items-center gap-3">
                <span :class="[
                  'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                  investmentsSummary.totalReturnPercent >= 0 ? 'text-primary' : 'text-destructive'
                ]">
                  <ArrowUpRight v-if="investmentsSummary.totalReturnPercent >= 0" class="size-3.5" />
                  <ArrowDownRight v-else class="size-3.5" />
                  {{ investmentsSummary.totalReturnPercent > 0 ? '+' : '' }}{{ investmentsSummary.totalReturnPercent.toFixed(1) }}%
                </span>
                <span class="text-sm text-muted-foreground">all time</span>
                <span class="h-4 w-px bg-border" aria-hidden="true" />
                <span :class="[
                  'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                  investmentsSummary.dayChangePercent >= 0 ? 'text-primary' : 'text-destructive'
                ]">
                  <ArrowUpRight v-if="investmentsSummary.dayChangePercent >= 0" class="size-3.5" />
                  <ArrowDownRight v-else class="size-3.5" />
                  {{ investmentsSummary.dayChangePercent > 0 ? '+' : '' }}{{ investmentsSummary.dayChangePercent.toFixed(1) }}%
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

        <Card class="border-border">
          <CardHeader>
            <CardTitle class="text-base">Summary</CardTitle>
            <CardDescription>Capital and gains</CardDescription>
          </CardHeader>
          <CardContent class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Invested</span>
              <span class="font-semibold tabular-nums text-foreground">
                {{ formatCurrency(investmentsSummary.investedAmount) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Current value</span>
              <span class="font-semibold tabular-nums text-foreground">
                {{ formatCurrency(investmentsSummary.totalValue) }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Total gain</span>
              <span class="font-semibold tabular-nums text-primary">
                {{ formatCurrency(investmentsSummary.totalValue - investmentsSummary.investedAmount) }}
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
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                <component :is="categoryIcons[cat.icon]" class="size-5" />
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
              {{ formatCurrency(cat.value) }}
            </p>
          </button>
        </div>
      </section>

      <!-- Holdings for active category -->
      <section class="mt-8">
        <div class="mb-3 flex items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            {{ activeCategories.find(c => c.id === activeCat)?.label }} holdings
          </h2>
          <Badge variant="secondary">{{ holdings.length }}</Badge>
        </div>
        <Card class="border-border">
          <CardContent class="divide-y divide-border p-0">
            <div
              v-for="h in holdings"
              :key="h.id"
              class="flex items-center gap-4 px-4 py-4 sm:px-6"
            >
              <span :class="[
                'flex size-10 items-center justify-center rounded-xl text-sm font-semibold',
                h.returnPercent >= 0 ? 'bg-primary/15 text-primary' : 'bg-destructive/15 text-destructive'
              ]">
                <TrendingUp v-if="h.returnPercent >= 0" class="size-5" />
                <TrendingDown v-else class="size-5" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-foreground">
                  {{ h.name }}
                </p>
                <p class="text-sm text-muted-foreground">{{ h.ticker }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-foreground tabular-nums">
                  {{ formatCurrency(h.value) }}
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
                  <span class="text-xs text-muted-foreground">total</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  </DashboardLayout>
</template>
