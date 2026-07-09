<script setup lang="ts">
import { ref } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useChartTheme } from '@/lib/chartTheme'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  BarChart,
  CanvasRenderer
])

const chartData = [1200, 2400, 3100, 4800, 12500]
const totalSpending = chartData.reduce((acc, curr) => acc + curr, 0)

const { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, getTranslucentStyle } = useChartTheme()
const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...commonTooltip,
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (params: any) => {
      const val = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(params[0].value)
      return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span>`
    }
  },
  grid: { 
    ...commonGrid,
    left: 80,
    right: '5%' 
  },
  xAxis: {
    ...commonXAxis,
    type: 'value',
    splitLine: { 
      show: true,
      lineStyle: { type: 'dashed', color: CHART_COLORS.gridLine }
    },
    axisLabel: { ...commonXAxis.axisLabel, formatter: (value: number) => value >= 1000 ? `${value / 1000}K` : value }
  },
  yAxis: {
    ...commonYAxis,
    type: 'category',
    data: ['Subscriptions', 'Transport', 'Restaurants', 'Groceries', 'Rent'],
    splitLine: { show: false },
    axisLabel: { ...commonYAxis.axisLabel, color: CHART_COLORS.textSecondary }
  },
  series: [
    {
      name: 'Amount',
      type: 'bar',
      barWidth: '40%',
      data: chartData,
      itemStyle: {
        ...getTranslucentStyle(CHART_COLORS.primary),
        borderRadius: [0, 4, 4, 0]
      },
      emphasis: {
        itemStyle: { color: '#45b8ff' }
      },
      animationDuration: 400,
      animationEasing: 'cubicOut'
    }
  ]
})
</script>

<template>
  <Card class="border-border/50 bg-card flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-muted-foreground">Top Spending Categories</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-foreground tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalSpending) }}</span>
      </div>
      <CardDescription class="text-muted-foreground">This month</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <VChart class="w-full h-full" :option="chartOption" autoresize />
    </CardContent>
  </Card>
</template>
