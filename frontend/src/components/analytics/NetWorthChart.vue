<script setup lang="ts">
import { ref } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { netWorthEvolution } from '@/lib/data'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, commonLineSeriesProps, getAreaGradient } from '@/lib/chartTheme'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const currentNetWorth = netWorthEvolution[netWorthEvolution.length - 1].value

const option = ref({
  tooltip: {
    ...commonTooltip,
    trigger: 'axis',
    formatter: (params: any) => {
      const v = params[0].value
      const formatted = new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)
      return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">$${formatted}</span>`
    },
    axisPointer: {
      type: 'line',
      lineStyle: { color: 'rgba(255,255,255,0.1)', width: 1 }
    }
  },
  grid: commonGrid,
  xAxis: {
    ...commonXAxis,
    type: 'category',
    data: netWorthEvolution.map(item => item.month),
  },
  yAxis: {
    ...commonYAxis,
    type: 'value',
    axisLabel: {
      ...commonYAxis.axisLabel,
      formatter: (v: number) => `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)}`
    }
  },
  series: [
    {
      data: netWorthEvolution.map(item => item.value),
      type: 'line',
      ...commonLineSeriesProps,
      areaStyle: {
        color: getAreaGradient()
      }
    }
  ]
})
</script>

<template>
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Net Worth Evolution</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">${{ new Intl.NumberFormat('en-US').format(currentNetWorth) }}</span>
      </div>
      <CardDescription class="text-[#6b7280]">Last 9 months</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <VChart class="w-full h-full" :option="option" autoresize />
    </CardContent>
  </Card>
</template>
