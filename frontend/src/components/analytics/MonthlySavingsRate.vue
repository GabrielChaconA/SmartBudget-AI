<script setup lang="ts">
import { ref } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, commonLineSeriesProps, getAreaGradient } from '@/lib/chartTheme'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LineChart,
  CanvasRenderer
])

const chartData = [16, 18, 22, 19, 23, 25]
const currentRate = chartData[chartData.length - 1]

const chartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    ...commonTooltip,
    trigger: 'axis',
    formatter: (params: any) => {
      return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${params[0].value}%</span>`
    },
    axisPointer: {
      type: 'line',
      lineStyle: { color: 'rgba(255,255,255,0.1)', width: 1 }
    }
  },
  grid: {
    ...commonGrid,
    left: 40,
    bottom: 20
  },
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
      formatter: '{value}%'
    }
  },
  series: [
    {
      data: chartData,
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
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Monthly Savings Rate</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">{{ currentRate }}%</span>
      </div>
      <CardDescription class="text-[#6b7280]">Percentage of income saved</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <VChart class="w-full h-full" :option="chartOption" autoresize />
    </CardContent>
  </Card>
</template>
