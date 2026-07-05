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
import { CHART_COLORS, getTranslucentStyle } from '@/lib/chartTheme'

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  PieChart,
  CanvasRenderer
])

const isLoading = ref(false)
const isError = ref(false)

const defaultData = [
  { value: 15, name: 'Bonds' },
  { value: 10, name: 'Crypto' },
  { value: 27, name: 'ETFs' },
  { value: 48, name: 'Stocks' }
]

const chartData = ref(defaultData.sort((a, b) => b.value - a.value).map((item, idx) => ({
  ...item,
  itemStyle: { ...getTranslucentStyle(CHART_COLORS.pieColors[idx % CHART_COLORS.pieColors.length]) }
})))

const totalValue = computed(() => {
  return chartData.value.reduce((acc, curr) => acc + curr.value, 0)
})

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    backgroundColor: CHART_COLORS.tooltipBg,
    borderColor: CHART_COLORS.tooltipBorder,
    borderRadius: 8,
    padding: [8, 12],
    trigger: 'item',
    formatter: (params: any) => {
      const val = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(params.value)
      return `<span style="color:${CHART_COLORS.textSecondary}">${params.name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span> <span style="font-size:12px;color:${CHART_COLORS.textTertiary}">(${params.percent}%)</span>`
    }
  },
  legend: {
    bottom: '0%',
    left: 'center',
    textStyle: { color: CHART_COLORS.textSecondary },
    icon: 'circle',
    itemGap: 16
  },
  series: [
    {
      name: 'Allocation',
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: CHART_COLORS.textPrimary,
          fontFamily: 'Inter, Geist, sans-serif'
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
      const rawData = [
        { value: Math.round(betsValue), name: 'Bets' },
        { value: Math.round(cryptoValue), name: 'Crypto' },
        { value: Math.round(etfValue), name: 'ETFs' },
        { value: Math.round(stockValue), name: 'Stocks' }
      ]
      
      chartData.value = rawData
        .filter(item => item.value > 0)
        .sort((a, b) => b.value - a.value)
        .map((item, idx) => ({
          ...item,
          itemStyle: { ...getTranslucentStyle(CHART_COLORS.pieColors[idx % CHART_COLORS.pieColors.length]) }
        }))
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
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none p-2 sm:p-4 relative">
    <CardHeader class="pb-2 flex flex-row items-start justify-between">
      <div class="flex flex-col">
        <CardTitle class="text-base font-normal text-[#a1a1aa]">Investment Allocation</CardTitle>
        <div class="mt-1 flex items-baseline gap-2">
           <span class="text-3xl font-bold text-white tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalValue) }}</span>
        </div>
        <CardDescription class="text-[#6b7280]">Portfolio breakdown</CardDescription>
      </div>
      <div v-if="isLoading" class="text-[#a1a1aa] animate-spin">
        <RefreshCw class="size-4" />
      </div>
      <div v-else-if="isError" class="text-destructive flex items-center">
        <AlertCircle class="size-4 mr-1" />
      </div>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4 flex items-center justify-center">
      <VChart class="w-full h-full" :option="chartOption" autoresize />
    </CardContent>
  </Card>
</template>
