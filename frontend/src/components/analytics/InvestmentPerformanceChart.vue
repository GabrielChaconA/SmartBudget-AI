<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useInvestments } from '@/composables/useInvestments'
import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, getTranslucentStyle } from '@/lib/chartTheme'

echarts.use([TooltipComponent, GridComponent, BarChart, CanvasRenderer])

const { allHoldings } = useInvestments()

const chartOption = computed(() => {
  const topHoldings = [...allHoldings.value]
    .sort((a, b) => b.returnPercent - a.returnPercent)
    .slice(0, 8)

  const names = topHoldings.map(h => h.ticker)
  const values = topHoldings.map(h => h.returnPercent)

  return {
    tooltip: {
      ...commonTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = params[0].value
        const color = val >= 0 ? CHART_COLORS.positive : CHART_COLORS.negative
        return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${color};font-weight:700;font-size:14px;">${val}%</span>`
      }
    },
    grid: {
      ...commonGrid,
      top: 30,
      left: 16,
      right: 16,
      bottom: 0,
      containLabel: true
    },
    xAxis: {
      ...commonXAxis,
      type: 'category',
      data: names,
      splitLine: { show: false },
      axisLabel: { 
        ...commonXAxis.axisLabel, 
        color: CHART_COLORS.textSecondary,
        interval: 0,
        rotate: 30 // rotate labels slightly if they don't fit
      }
    },
    yAxis: {
      ...commonYAxis,
      type: 'value',
      splitLine: {
        show: true,
        lineStyle: { type: 'dashed', color: CHART_COLORS.gridLine }
      },
      axisLabel: { ...commonYAxis.axisLabel, formatter: '{value}%' }
    },
    series: [
      {
        name: 'Rendimiento',
        type: 'bar',
        barWidth: '40%',
        data: values.map((val) => {
          const isPos = val >= 0
          return {
            value: val,
            itemStyle: {
              ...getTranslucentStyle(isPos ? CHART_COLORS.positive : CHART_COLORS.negative),
              borderRadius: isPos ? [4, 4, 0, 0] : [0, 0, 4, 4]
            }
          }
        }),
        emphasis: {
          itemStyle: {
            color: CHART_COLORS.primary
          }
        },
        animationDuration: 400,
        animationEasing: 'cubicOut'
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none overflow-hidden pt-4 sm:pt-6">
    <CardHeader class="px-4 sm:px-6 pb-2">
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Rendimiento de Inversiones</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">Top 8</span>
      </div>
      <CardDescription class="text-[#6b7280]">Ganancias y pérdidas principales (%)</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <VChart :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>

