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

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  PieChart,
  CanvasRenderer
])

const chartOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    bottom: '0%',
    left: 'center',
    textStyle: { color: '#a1a1aa' },
    icon: 'square'
  },
  series: [
    {
      name: 'Allocation',
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderColor: '#18181b',
        borderWidth: 0
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: '#f5f5f5'
        }
      },
      labelLine: { show: false },
      data: [
        { value: 15, name: 'Bonds', itemStyle: { color: '#52525b' } },
        { value: 10, name: 'Crypto', itemStyle: { color: '#a1a1aa' } },
        { value: 27, name: 'ETFs', itemStyle: { color: '#4ade80' } },
        { value: 48, name: 'Stocks', itemStyle: { color: '#22c55e' } }
      ]
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Investment Allocation</CardTitle>
      <CardDescription>Portfolio breakdown</CardDescription>
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
