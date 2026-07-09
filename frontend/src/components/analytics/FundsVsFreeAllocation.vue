<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { CHART_COLORS, getTranslucentStyle } from '@/lib/chartTheme'
import { exchangeRateService } from '@/services/exchangeRate'

echarts.use([TooltipComponent, LegendComponent, PieChart, CanvasRenderer])

const { freeMoney, user } = useUser()
const props = defineProps<{
  displayCurrency: string
}>()

const exchangeRate = ref(20.0)
onMounted(async () => {
  exchangeRate.value = await exchangeRateService.getUsdMxnRate()
})

const convertToDisplay = (val: number) => {
  const userCur = user.value?.currency || 'MXN'
  if (userCur === props.displayCurrency) return val
  if (userCur === 'MXN' && props.displayCurrency === 'USD') return val / exchangeRate.value
  if (userCur === 'USD' && props.displayCurrency === 'MXN') return val * exchangeRate.value
  return val
}

const totalMoney = computed(() => {
  const fundsTotal = (user.value?.funds || []).reduce((acc: number, f: any) => acc + parseFloat(f.balance), 0)
  const val = freeMoney.value + fundsTotal
  return convertToDisplay(val)
})

const chartOption = computed(() => {
  const fundsData = (user.value?.funds || []).map((f: any) => ({
    value: convertToDisplay(parseFloat(f.balance)),
    name: f.name || 'Caja'
  })).filter((item: any) => item.value > 0)

  let rawData = [
    { value: convertToDisplay(freeMoney.value), name: 'Dinero Libre' },
    ...fundsData
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
          currency: props.displayCurrency
        }).format(params.value)
        return `<span style="color:${CHART_COLORS.textSecondary}">${params.name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span> <span style="font-size:12px;color:${CHART_COLORS.textTertiary}">(${params.percent}%)</span>`
      }
    },
    legend: {
      type: 'scroll',
      bottom: '0%',
      left: 'center',
      textStyle: { color: CHART_COLORS.textSecondary },
      icon: 'circle',
      itemGap: 16
    },
    series: [
      {
        name: 'Dinero Disponible',
        type: 'pie',
        radius: ['45%', '75%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8
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
      <CardTitle class="text-base font-normal text-[#a1a1aa]">Dinero Disponible</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-white tracking-tight">{{ new Intl.NumberFormat('en-US', { style: 'currency', currency: displayCurrency }).format(totalMoney) }}</span>
      </div>
      <CardDescription class="text-[#6b7280]">Cajas (Funds) vs Dinero Libre</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4 flex items-center justify-center">
      <div v-if="freeMoney === 0 && (user?.funds || []).length === 0" class="text-[#6b7280] text-sm">
        No hay datos suficientes
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
