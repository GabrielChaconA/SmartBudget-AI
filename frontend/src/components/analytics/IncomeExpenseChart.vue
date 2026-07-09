<script setup lang="ts">
import { ref, computed } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useChartTheme } from '@/lib/chartTheme'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  CanvasRenderer
])

const incomeData = [45000, 48000, 47000, 50000, 48000, 52000]
const expenseData = [18000, 19000, 17500, 16000, 18500, 19000]

const totalIncome = computed(() => incomeData.reduce((a, b) => a + b, 0))
const totalExpense = computed(() => expenseData.reduce((a, b) => a + b, 0))

const { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis } = useChartTheme()
const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...commonTooltip,
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  legend: {
    data: ['Income', 'Expenses'],
    textStyle: { color: CHART_COLORS.textSecondary },
    bottom: 0,
    icon: 'circle',
    itemWidth: 8,
    itemHeight: 8
  },
  grid: commonGrid,
  xAxis: {
    ...commonXAxis,
    type: 'category',
    data: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
  },
  yAxis: {
    ...commonYAxis,
    type: 'value',
    axisLabel: {
      ...commonYAxis.axisLabel,
      formatter: (value: number) => `$${value}`
    }
  },
  series: [
    {
      name: 'Income',
      type: 'bar',
      data: incomeData,
      itemStyle: {
        color: CHART_COLORS.positive,
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '30%'
    },
    {
      name: 'Expenses',
      type: 'bar',
      data: expenseData,
      itemStyle: {
        color: '#52525b', // dark gray
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '30%'
    }
  ],
  animationDuration: 1000,
  animationEasing: 'cubicOut'
}))
</script>

<template>
  <Card class="border-border/50 bg-card flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-muted-foreground">Income vs Expenses</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-foreground tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalIncome) }}</span>
         <span class="text-sm font-medium text-muted-foreground">vs ${{ new Intl.NumberFormat('en-US').format(totalExpense) }}</span>
      </div>
      <CardDescription class="text-muted-foreground">Monthly comparison</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <VChart class="w-full h-full" :option="chartOption" autoresize />
    </CardContent>
  </Card>
</template>
