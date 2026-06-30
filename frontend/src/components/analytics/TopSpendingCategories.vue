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

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  BarChart,
  CanvasRenderer
])

const chartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    splitLine: { show: false },
    axisLabel: { color: '#a1a1aa', formatter: (value: number) => value >= 1000 ? `${value / 1000}K` : value }
  },
  yAxis: {
    type: 'category',
    data: ['Subscriptions', 'Transport', 'Restaurants', 'Groceries', 'Rent'],
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#a1a1aa' }
  },
  series: [
    {
      name: 'Amount',
      type: 'bar',
      data: [1200, 2400, 3100, 4800, 12500],
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => {
          const colors = ['#22c55e', '#52525b', '#a1a1aa', '#4ade80', '#22c55e'].reverse()
          return colors[params.dataIndex]
        }
      }
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Top Spending Categories</CardTitle>
      <CardDescription>This month</CardDescription>
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
