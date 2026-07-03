<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { investmentHoldings } from '@/lib/data'

echarts.use([TooltipComponent, GridComponent, BarChart, CanvasRenderer])

const chartOption = computed(() => {
  // Combine some holdings to show a mix of positive and negative
  const allHoldings = [
    ...investmentHoldings.stocks,
    ...investmentHoldings.etfs,
    ...investmentHoldings.bets
  ].sort((a, b) => b.returnPercent - a.returnPercent).slice(0, 8)

  const names = allHoldings.map(h => h.ticker)
  const values = allHoldings.map(h => h.returnPercent)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = params[0].value
        const color = val >= 0 ? '#22c55e' : '#ef4444'
        return `${params[0].name}<br/><span style="color:${color};font-weight:bold;">${val}%</span>`
      }
    },
    grid: {
      top: 30,
      bottom: 30,
      left: 40,
      right: 20
    },
    xAxis: {
      type: 'value',
      position: 'top',
      splitLine: {
        lineStyle: { type: 'dashed', color: '#27272a' }
      },
      axisLabel: { formatter: '{value}%', color: '#a1a1aa' }
    },
    yAxis: {
      type: 'category',
      axisLine: { show: false },
      axisLabel: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      data: names
    },
    series: [
      {
        name: 'Rendimiento',
        type: 'bar',
        data: values.map((val, idx) => {
          const isPos = val >= 0
          return {
            value: val,
            label: {
              show: true,
              position: isPos ? 'right' : 'left',
              formatter: '{b}',
              color: '#f4f4f5'
            },
            itemStyle: {
              color: isPos ? '#22c55e' : '#14532d',
              borderRadius: 4
            }
          }
        })
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border flex flex-col">
    <CardHeader class="pb-2">
      <CardTitle class="text-base">Rendimiento de Inversiones</CardTitle>
      <CardDescription>Ganancias y pérdidas principales (%)</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-4">
      <VChart :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
