<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { CHART_COLORS, getTranslucentStyle } from '@/lib/chartTheme'

echarts.use([TooltipComponent, LegendComponent, PieChart, CanvasRenderer])

const { freeMoney, totalSubscriptionsAmount, totalInvestmentsAmount, user } = useUser()

const chartOption = computed(() => {
  const free = freeMoney.value
  const subs = totalSubscriptionsAmount.value
  const inv = totalInvestmentsAmount.value

  let rawData = [
    { value: free, name: 'Dinero Libre' },
    { value: subs, name: 'Suscripciones' },
    { value: inv, name: 'Inversiones' }
  ].filter(item => item.value > 0)

  // Sort descending so largest is brightest green
  rawData.sort((a, b) => b.value - a.value)

  const data = rawData.map((item, idx) => ({
    ...item,
    itemStyle: { ...getTranslucentStyle(CHART_COLORS.pieColors[idx % CHART_COLORS.pieColors.length]) }
  }))

  return {
    tooltip: {
      backgroundColor: CHART_COLORS.tooltipBg,
      borderColor: CHART_COLORS.tooltipBorder,
      borderRadius: 8,
      padding: [8, 12],
      trigger: 'item',
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: user.value?.currency || 'MXN'
        }).format(params.value)
        return `<span style="color:${CHART_COLORS.textSecondary}">${params.name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span> <span style="font-size:12px;color:${CHART_COLORS.textTertiary}">(${params.percent}%)</span>`
      }
    },
    legend: {
      bottom: '0%',
      left: 'center',
      textStyle: { color: CHART_COLORS.textSecondary },
      icon: 'circle',
      itemGap: 24,
    },
    series: [
      {
        name: 'Distribución',
        type: 'pie',
        radius: ['45%', '75%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8 // Soft corners only, colors handled per item
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: CHART_COLORS.textPrimary,
            fontFamily: 'Inter, Geist, sans-serif'
          }
        },
        labelLine: { show: false },
        data
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Distribución Global</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">${{ new Intl.NumberFormat('en-US').format(freeMoney + totalSubscriptionsAmount + totalInvestmentsAmount) }}</span>
      </div>
      <CardDescription class="text-[#6b7280]">Dinero libre vs Suscripciones vs Inversiones</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4 flex items-center justify-center">
      <div v-if="freeMoney === 0 && totalSubscriptionsAmount === 0 && totalInvestmentsAmount === 0" class="text-[#6b7280] text-sm">
        No hay datos suficientes
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
