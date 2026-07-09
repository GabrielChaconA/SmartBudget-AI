<script setup lang="ts">
import { ref } from 'vue'
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
import { useChartTheme } from '@/lib/chartTheme'

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  PieChart,
  CanvasRenderer
])

const rawData = [
  { value: 1200, name: 'Housing' },
  { value: 600, name: 'Food' },
  { value: 400, name: 'Transport' },
  { value: 300, name: 'Entertainment' },
  { value: 200, name: 'Other' }
]
const chartData = rawData.sort((a, b) => b.value - a.value).map((item, idx) => ({
  ...item,
  itemStyle: { ...getTranslucentStyle(CHART_COLORS.pieColors[idx % CHART_COLORS.pieColors.length]) }
}))
const totalSpending = chartData.reduce((acc, curr) => acc + curr.value, 0)

const { CHART_COLORS, getTranslucentStyle } = useChartTheme()
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
      name: 'Category',
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: CHART_COLORS.textPrimary,
          fontFamily: 'Inter, Geist, sans-serif'
        }
      },
      labelLine: {
        show: false
      },
      data: chartData
    }
  ]
}))
</script>

<template>
  <Card class="border-border/50 bg-card flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-muted-foreground">Spending by Category</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-foreground tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalSpending) }}</span>
      </div>
      <CardDescription class="text-muted-foreground">Where your money went this month</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4 flex items-center justify-center">
      <VChart class="w-full h-full" :option="chartOption" autoresize />
    </CardContent>
  </Card>
</template>
