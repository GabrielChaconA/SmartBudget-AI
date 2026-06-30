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

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LineChart,
  CanvasRenderer
])

const chartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    formatter: '{b}: {c}%'
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#a1a1aa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#27272a', type: 'dashed' } },
    axisLabel: {
      color: '#a1a1aa',
      formatter: '{value}%'
    }
  },
  series: [
    {
      data: [16, 18, 22, 19, 23, 25],
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#22c55e', borderColor: '#18181b', borderWidth: 1 },
      lineStyle: { color: '#22c55e', width: 2 }
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Monthly Savings Rate</CardTitle>
      <CardDescription>Percentage of income saved</CardDescription>
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
