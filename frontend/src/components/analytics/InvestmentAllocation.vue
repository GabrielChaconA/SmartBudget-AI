<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { RefreshCw, AlertCircle } from '@lucide/vue'
import { investmentHoldings as fallbackHoldings } from '@/lib/data'
import { finnhubService } from '@/services/finnhub'
import { coingeckoService } from '@/services/coingecko'
import { oddsApiService } from '@/services/oddsApi'

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  PieChart,
  CanvasRenderer
])

const isLoading = ref(false)
const isError = ref(false)
const chartData = ref([
  { value: 15, name: 'Bonds', itemStyle: { color: '#52525b' } },
  { value: 10, name: 'Crypto', itemStyle: { color: '#a1a1aa' } },
  { value: 27, name: 'ETFs', itemStyle: { color: '#4ade80' } },
  { value: 48, name: 'Stocks', itemStyle: { color: '#22c55e' } }
])

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    bottom: '0%',
    left: 'center',
    textStyle: { color: '#a1a1aa' },
    icon: 'square'
  },
  series: [
    {
      name: 'Allocation',
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderColor: '#18181b',
        borderWidth: 0
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: '#f5f5f5'
        }
      },
      labelLine: { show: false },
      data: chartData.value
    }
  ]
}))

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
    
    let etfValue = 0
    if (etfRes.status === 'fulfilled') {
      etfValue = etfRes.value.reduce((sum, item) => sum + (item.q.c > 0 ? item.q.c * (item.h.value / 100) : item.h.value), 0)
    }
    
    let stockValue = 0
    if (stockRes.status === 'fulfilled') {
      stockValue = stockRes.value.reduce((sum, item) => sum + (item.q.c > 0 ? item.q.c * (item.h.value / 100) : item.h.value), 0)
    }
    
    let cryptoValue = 0
    if (cryptoRes.status === 'fulfilled' && cryptoRes.value.length > 0) {
      cryptoValue = fallbackHoldings.crypto.reduce((sum, c) => {
        const market = cryptoRes.value.find(m => m.symbol.toLowerCase() === c.ticker.toLowerCase())
        return sum + (market ? market.current_price * (c.value / 1000) : c.value)
      }, 0)
    }
    
    let betsValue = 0
    if (oddsRes.status === 'fulfilled' && oddsRes.value.length > 0) {
      betsValue = oddsRes.value.slice(0, 3).reduce((sum, e, i) => sum + (fallbackHoldings.bets[i]?.value || fallbackHoldings.bets[0].value), 0)
    }

    if (etfValue || stockValue || cryptoValue || betsValue) {
      chartData.value = [
        { value: Math.round(betsValue), name: 'Bets', itemStyle: { color: '#52525b' } },
        { value: Math.round(cryptoValue), name: 'Crypto', itemStyle: { color: '#a1a1aa' } },
        { value: Math.round(etfValue), name: 'ETFs', itemStyle: { color: '#4ade80' } },
        { value: Math.round(stockValue), name: 'Stocks', itemStyle: { color: '#22c55e' } }
      ]
    }
  } catch {
    isError.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <Card class="bg-card border-border relative">
    <CardHeader class="flex flex-row items-start justify-between">
      <div>
        <CardTitle class="text-foreground">Investment Allocation</CardTitle>
        <CardDescription>Portfolio breakdown</CardDescription>
      </div>
      <div v-if="isLoading" class="text-muted-foreground animate-spin">
        <RefreshCw class="size-4" />
      </div>
      <div v-else-if="isError" class="text-destructive flex items-center">
        <AlertCircle class="size-4 mr-1" />
      </div>
    </CardHeader>
    <CardContent>
      <div class="h-[250px] w-full">
        <VChart class="chart" :option="chartOption" autoresize />
      </div>
    </CardContent>
  </Card>
</template>

<style scoped>
.chart {
  height: 100%;
  width: 100%;
}
</style>
