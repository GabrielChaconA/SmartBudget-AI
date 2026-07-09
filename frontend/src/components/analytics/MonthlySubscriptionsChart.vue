<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useChartTheme } from '@/lib/chartTheme'
import { exchangeRateService } from '@/services/exchangeRate'

echarts.use([TooltipComponent, GridComponent, BarChart, CanvasRenderer])

const { user } = useUser()
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

const totalSubscriptionsCost = computed(() => {
  const total = (user.value?.subscriptions || [])
    .filter((s: any) => s.status !== 'inactive')
    .reduce((acc, s) => acc + (s.billing_cycle === 'yearly' ? parseFloat(s.amount) / 12 : parseFloat(s.amount)), 0)
  return convertToDisplay(total)
})

const { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, getTranslucentStyle } = useChartTheme()
const chartOption = computed(() => {
  // Only active subscriptions
  const subs = (user.value?.subscriptions || [])
    .filter((s: any) => s.status !== 'inactive')
    .map((s: any) => {
      // Calculate monthly equivalent
      let monthlyCost = s.billing_cycle === 'yearly' ? parseFloat(s.amount) / 12 : parseFloat(s.amount)
      monthlyCost = convertToDisplay(monthlyCost)
      return { name: s.name, cost: monthlyCost }
    })
    .sort((a, b) => a.cost - b.cost) // Sort ascending for horizontal bar (largest at top)

  const names = subs.map(s => s.name)
  const values = subs.map(s => s.cost)

  return {
    tooltip: {
      ...commonTooltip,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: props.displayCurrency
        }).format(params[0].value)
        return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val} <span style="font-size:12px;color:${CHART_COLORS.textTertiary}">/ mes</span></span>`
      }
    },
    grid: {
      ...commonGrid,
      top: 10,
      left: 16,
      right: 16,
      bottom: 0,
      containLabel: true
    },
    xAxis: {
      ...commonXAxis,
      type: 'value',
      splitLine: {
        show: true,
        lineStyle: { type: 'dashed', color: CHART_COLORS.gridLine }
      }
    },
    yAxis: {
      ...commonYAxis,
      type: 'category',
      data: names,
      splitLine: { show: false },
      axisLabel: { 
        ...commonYAxis.axisLabel,
        color: CHART_COLORS.textSecondary, 
        width: 80, 
        overflow: 'truncate' 
      },
    },
    series: [
      {
        name: 'Costo Mensual',
        type: 'bar',
        barWidth: '40%',
        data: values,
        itemStyle: {
          ...getTranslucentStyle(CHART_COLORS.primary),
          borderRadius: [0, 4, 4, 0]
        },
        emphasis: {
          itemStyle: { color: CHART_COLORS.primary }
        },
        label: {
          show: false // Hidden since we have tooltip and X axis
        },
        animationDuration: 400,
        animationEasing: 'cubicOut'
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border/50 bg-card flex flex-col rounded-[20px] shadow-none overflow-hidden pt-4 sm:pt-6">
    <CardHeader class="px-4 sm:px-6 pb-2">
      <CardTitle class="text-base font-normal text-muted-foreground">Gasto en Suscripciones</CardTitle>
      <div class="mt-1 flex items-baseline gap-2">
         <span class="text-3xl font-bold text-foreground tracking-tight">${{ new Intl.NumberFormat('en-US').format(totalSubscriptionsCost) }}</span>
         <span class="text-sm font-medium text-muted-foreground">/ mes</span>
      </div>
      <CardDescription class="text-muted-foreground">Costo mensual por suscripción activa</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4">
      <div v-if="(user?.subscriptions || []).length === 0" class="text-muted-foreground text-sm flex h-full items-center justify-center">
        No hay suscripciones activas
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
