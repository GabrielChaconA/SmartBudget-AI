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
    formatter: '{a} <br/>{b}: ${c} ({d}%)'
  },
  legend: {
    bottom: '0%',
    left: 'center',
    textStyle: { color: '#a1a1aa' }
  },
  series: [
    {
      name: 'Category',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#161616',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold',
          color: '#f5f5f5'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 1200, name: 'Housing', itemStyle: { color: '#22c55e' } },
        { value: 600, name: 'Food', itemStyle: { color: '#4ade80' } },
        { value: 400, name: 'Transport', itemStyle: { color: '#16a34a' } },
        { value: 300, name: 'Entertainment', itemStyle: { color: '#a1a1aa' } },
        { value: 200, name: 'Other', itemStyle: { color: '#525252' } }
      ]
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Spending by Category</CardTitle>
      <CardDescription>Where your money went this month</CardDescription>
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
