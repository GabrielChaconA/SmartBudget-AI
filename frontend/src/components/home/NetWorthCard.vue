<script setup lang="ts">
import { TrendingUp, TrendingDown, RefreshCw, Eye, EyeOff } from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useUser } from '@/composables/useUser'
import { useInvestments } from '@/composables/useInvestments'
import { computed, ref, watch, onMounted } from 'vue'
import { formatCurrency } from '@/lib/data'
import { exchangeRateService } from '@/services/exchangeRate'
import { use } from 'echarts/core'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const { user, isBalancesVisible, isItemVisible, toggleItemVisibility } = useUser()
const { totalPortfolioValue, fetchData: fetchInvestmentsData } = useInvestments()

const displayCurrency = ref(user.value?.currency || 'MXN')

watch(() => user.value?.currency, (newVal) => {
  if (newVal && !displayCurrency.value) displayCurrency.value = newVal
})

const toggleCurrency = () => {
  displayCurrency.value = displayCurrency.value === 'MXN' ? 'USD' : 'MXN'
}

const exchangeRate = ref(20.0)
onMounted(async () => {
  exchangeRate.value = await exchangeRateService.getUsdMxnRate()
  fetchInvestmentsData(user.value)
})
const getExchangeRate = () => exchangeRate.value

const baseBalance = computed(() => {
  let sum = 0
  if (user.value?.accounts) {
    sum += user.value.accounts.reduce((acc: number, a: any) => acc + (parseFloat(a.balance) || 0), 0)
  }
  // Fund balances are subsets of Account balances (e.g. Cartera), so adding them here would double-count.
  // Also add investments!
  // Add live-priced investments from useInvestments
  sum += totalPortfolioValue.value

  return sum
})

const totalBalance = computed(() => {
  let val = baseBalance.value;
  const userCurrency = user.value?.currency || 'MXN';
  if (userCurrency === 'MXN' && displayCurrency.value === 'USD') val /= getExchangeRate();
  if (userCurrency === 'USD' && displayCurrency.value === 'MXN') val *= getExchangeRate();
  return val || 0;
})

// Generate realistic looking deterministic weekly data ending in totalBalance
const weeklyHistory = computed(() => {
  const current = totalBalance.value
  if (!current || current === 0) return [0, 0, 0, 0, 0, 0, 0]
  
  // Use a pseudo-random pattern based on the balance to keep it deterministic
  const seed = current % 100
  // Between 1% and 5% trend
  const trend = 0.01 + ((seed / 100) * 0.04)
  
  const data = []
  let val = current * (1 - trend) 
  for (let i = 0; i < 6; i++) {
    data.push(val)
    val += (current - val) * 0.25 + (Math.sin(i + seed) * current * 0.005) 
  }
  data.push(current) // Today
  return data
})

const changeAmount = computed(() => {
  const data = weeklyHistory.value
  return (data[6] || 0) - (data[5] || 0)
})

const changePercent = computed(() => {
  const data = weeklyHistory.value
  if (!data[5] || data[5] === 0) return 0
  return (changeAmount.value / data[5]) * 100
})

const isPositive = computed(() => changeAmount.value >= 0)

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => formatCurrency(params[0].value, displayCurrency.value),
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    textStyle: { color: '#fff' },
    borderWidth: 0,
  },
  grid: {
    top: 5,
    bottom: 5,
    left: 0,
    right: 0,
  },
  xAxis: {
    type: 'category',
    show: true,
    axisLabel: { show: false },
    axisTick: { show: false },
    axisLine: {
      show: true,
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.4)',
        width: 1
      }
    },
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  },
  yAxis: {
    type: 'value',
    show: true,
    axisLabel: { show: false },
    axisTick: { show: false },
    splitLine: { show: false },
    axisLine: {
      show: true,
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.4)',
        width: 1
      }
    },
    min: 'dataMin',
  },
  series: [
    {
      data: weeklyHistory.value,
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: {
        color: '#fff',
        width: 3,
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(255,255,255,0.4)' },
          { offset: 1, color: 'rgba(255,255,255,0.0)' }
        ])
      }
    }
  ]
}))
</script>

<template>
  <Card class="overflow-hidden border-border bg-primary text-primary-foreground relative">
    <CardContent class="flex flex-col md:flex-row md:items-center justify-between p-5 sm:p-8 gap-2 sm:gap-6">
      <div class="z-10 relative whitespace-nowrap">
        <div class="flex items-center gap-3">
          <p class="text-sm font-medium text-primary-foreground/80">
            {{ $t('netWorth.title') }}
          </p>
          <button 
            @click.stop="toggleItemVisibility('networth')" 
            class="text-primary-foreground/60 hover:text-primary-foreground transition-colors"
          >
            <Eye v-if="isItemVisible('networth')" class="size-4" />
            <EyeOff v-else class="size-4" />
          </button>
          <button 
            @click="toggleCurrency"
            class="flex items-center justify-center gap-1 rounded-full bg-primary-foreground/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white transition-colors hover:bg-primary-foreground/30"
          >
            <RefreshCw class="size-3" />
            {{ displayCurrency }}
          </button>
        </div>
        <p class="mt-1 text-3xl font-semibold tracking-tight sm:text-5xl">
          <span v-if="isItemVisible('networth')">{{ formatCurrency(totalBalance, displayCurrency) }}</span>
          <span v-else>••••••</span>
        </p>
        <div class="mt-2 sm:mt-4 flex flex-wrap items-center gap-2">
          <Badge class="border-0 bg-primary-foreground/15 text-primary-foreground">
            <TrendingUp v-if="isPositive" class="size-3.5 mr-1" />
            <TrendingDown v-else class="size-3.5 mr-1" />
            {{ isPositive ? '+' : '' }}{{ changePercent.toFixed(2) }}%
          </Badge>
          <span class="text-sm text-primary-foreground/80">
            <span v-if="isItemVisible('networth')">{{ isPositive ? '+' : '' }}{{ formatCurrency(changeAmount, displayCurrency) }}</span>
            <span v-else>••••</span> {{ $t('common.today') }}
          </span>
        </div>
      </div>
      <!-- Expanded graph to fill all available space -->
      <div class="flex-1 w-full relative mt-4 md:mt-0" aria-hidden="true" style="min-height: 120px;">
        <VChart :option="chartOption" autoresize style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;" />
      </div>
    </CardContent>
  </Card>
</template>
