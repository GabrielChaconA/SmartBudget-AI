<script setup lang="ts">
import { ref } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart, { THEME_KEY } from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  CanvasRenderer
])

const chartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['Income', 'Expenses'],
    textStyle: { color: '#a1a1aa' },
    bottom: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    axisLine: { lineStyle: { color: '#3f3f46' } },
    axisLabel: { color: '#a1a1aa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#27272a' } },
    axisLabel: {
      color: '#a1a1aa',
      formatter: (value: number) => `$${value}`
    }
  },
  series: [
    {
      name: 'Income',
      type: 'bar',
      data: [45000, 48000, 47000, 50000, 48000, 52000],
      itemStyle: {
        color: '#22c55e',
        borderRadius: [4, 4, 0, 0]
      }
    },
    {
      name: 'Expenses',
      type: 'bar',
      data: [18000, 19000, 17500, 16000, 18500, 19000],
      itemStyle: {
        color: '#a1a1aa',
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Income vs Expenses</CardTitle>
      <CardDescription>Monthly comparison</CardDescription>
    </CardHeader>
    <CardContent>
      <div class="h-[300px] w-full">
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
