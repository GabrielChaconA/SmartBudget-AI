<script setup lang="ts">
import { TrendingUp, TrendingDown } from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useUser } from '@/composables/useUser'
import { computed } from 'vue'
import { formatCurrency } from '@/lib/data'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const { user } = useUser()

const totalBalance = computed(() => {
  let sum = 0
  if (user.value?.accounts) {
    sum += user.value.accounts.reduce((acc: number, a: any) => acc + parseFloat(a.balance), 0)
  }
  if (user.value?.funds) {
    sum += user.value.funds.reduce((acc: number, f: any) => acc + parseFloat(f.balance), 0)
  }
  return sum
})

// Generate realistic looking deterministic weekly data ending in totalBalance
const weeklyHistory = computed(() => {
  const current = totalBalance.value
  if (current === 0) return [0, 0, 0, 0, 0, 0, 0]
  
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
  return data[6] - data[5]
})

const changePercent = computed(() => {
  const data = weeklyHistory.value
  if (data[5] === 0) return 0
  return (changeAmount.value / data[5]) * 100
})

const isPositive = computed(() => changeAmount.value >= 0)

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => formatCurrency(params[0].value, user.value?.currency || 'MXN'),
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
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255,255,255,0.4)' },
            { offset: 1, color: 'rgba(255,255,255,0.0)' }
          ]
        }
      }
    }
  ]
}))
</script>

<template>
  <Card class="overflow-hidden border-border bg-primary text-primary-foreground relative">
    <CardContent class="flex flex-col md:flex-row md:items-center justify-between p-5 sm:p-8 gap-2 sm:gap-6">
      <div class="z-10 relative">
        <p class="text-sm font-medium text-primary-foreground/80">
          Total Net Worth
        </p>
        <p class="mt-1 text-3xl font-semibold tracking-tight sm:text-5xl">
          {{ formatCurrency(totalBalance, user?.currency || 'MXN') }}
        </p>
        <div class="mt-2 sm:mt-4 flex flex-wrap items-center gap-2">
          <Badge class="border-0 bg-primary-foreground/15 text-primary-foreground">
            <TrendingUp v-if="isPositive" class="size-3.5 mr-1" />
            <TrendingDown v-else class="size-3.5 mr-1" />
            {{ isPositive ? '+' : '' }}{{ changePercent.toFixed(2) }}%
          </Badge>
          <span class="text-sm text-primary-foreground/80">
            {{ isPositive ? '+' : '' }}{{ formatCurrency(changeAmount, user?.currency || 'MXN') }} today
          </span>
        </div>
      </div>
      <div class="w-full h-[60px] sm:h-[80px] md:h-[100px] md:w-[300px] md:max-w-[40%] z-0 relative md:-mr-4 mt-2 md:mt-0" aria-hidden="true">
        <VChart :option="chartOption" autoresize />
      </div>
    </CardContent>
  </Card>
</template>
