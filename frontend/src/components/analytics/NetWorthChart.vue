<script setup lang="ts">
import { ref } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { netWorthEvolution } from '@/lib/data'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const option = ref({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any) => {
      const v = params[0].value
      return `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)}`
    }
  },
  grid: { left: 16, right: 16, top: 16, bottom: 16, containLabel: true },
  xAxis: {
    type: 'category',
    data: netWorthEvolution.map(item => item.month),
    axisLine: { show: false },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed', color: '#333' } },
    axisLabel: {
      formatter: (v: number) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)
    }
  },
  series: [
    {
      data: netWorthEvolution.map(item => item.value),
      type: 'line',
      smooth: true,
      showSymbol: false,
      itemStyle: { color: '#22c55e' }, // var(--chart-1) equivalent
      lineStyle: { width: 3 }
    }
  ]
})
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Net Worth Evolution</CardTitle>
      <CardDescription>Last 9 months</CardDescription>
    </CardHeader>
    <CardContent>
      <div class="h-[300px] w-full">
        <VChart class="chart" :option="option" autoresize />
      </div>
    </CardContent>
  </Card>
</template>
