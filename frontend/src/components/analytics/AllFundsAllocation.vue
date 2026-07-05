<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, getTranslucentStyle } from '@/lib/chartTheme'

echarts.use([TooltipComponent, GridComponent, BarChart, CanvasRenderer])

const { user } = useUser()

const totalFundsBalance = computed(() => {
  return (user.value?.funds || [])
    .reduce((acc, f) => acc + parseFloat(f.balance), 0)
})

const chartOption = computed(() => {
  const fundsData = (user.value?.funds || [])
    .map((f: any) => ({
      name: f.name || 'Caja',
      value: parseFloat(f.balance)
    }))
    .filter((f: any) => f.value > 0)
    .sort((a, b) => b.value - a.value) // Sort descending for standard vertical bars or ascending for horizontal

  const names = fundsData.map(f => f.name)
  const values = fundsData.map(f => f.value)

  return {
    tooltip: {
      ...commonTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: user.value?.currency || 'MXN'
        }).format(params[0].value)
        return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span>`
      }
    },
    grid: {
      ...commonGrid,
      bottom: 40,
    },
    xAxis: {
      ...commonXAxis,
      type: 'category',
      data: names
    },
    yAxis: {
      ...commonYAxis,
      type: 'value',
      axisLabel: {
        ...commonYAxis.axisLabel,
        formatter: (value: number) => `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)}`
      }
    },
    series: [
      {
        name: 'Balance',
        type: 'bar',
        barWidth: '30%',
        data: values,
        itemStyle: {
          ...getTranslucentStyle(CHART_COLORS.primary),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: { color: '#45b8ff' }
        },
        label: {
          show: true,
          position: 'top',
          color: CHART_COLORS.textSecondary,
          fontFamily: 'Inter, Geist, sans-serif',
          formatter: (params: any) => `$${Math.round(params.value)}`
        },
        animationDuration: 400,
        animationEasing: 'cubicOut'
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Balance de Cajas</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalFundsBalance) }}</span>
      </div>
      <CardDescription class="text-[#6b7280]">Dinero almacenado en cada caja individual</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <div v-if="(user?.funds || []).length === 0" class="text-[#6b7280] text-sm flex h-full items-center justify-center">
        No hay cajas creadas o con fondos
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
