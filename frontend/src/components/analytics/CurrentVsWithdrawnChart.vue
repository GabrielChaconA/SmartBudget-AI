<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CHART_COLORS, commonTooltip, commonGrid, getTranslucentStyle } from '@/lib/chartTheme'
import { useUser } from '@/composables/useUser'
import { exchangeRateService } from '@/services/exchangeRate'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  PieChart,
  BarChart,
  CanvasRenderer
])

const { user, fetchTransactionStats, freeMoney, totalFundsAmount } = useUser()

const props = defineProps<{
  displayCurrency: string
}>()
const exchangeRate = ref(20.0)

const transactions = ref<any[]>([])
const isLoading = ref(true)

const timeFrames = [
  { id: '7D', label: '7D', days: 7 },
  { id: '1M', label: '1M', days: 30 },
  { id: '1Y', label: '1A', days: 365 },
  { id: 'ALL', label: 'Todo', days: 0 }
]
const activeTimeFrame = ref('1M')

onMounted(async () => {
  exchangeRate.value = await exchangeRateService.getUsdMxnRate()
  transactions.value = await fetchTransactionStats()
  isLoading.value = false
})

// Simple conversion: value is always stored in user's currency.
// If displayCurrency differs from user's currency, convert.
const convertToDisplay = (val: number) => {
  const userCur = user.value?.currency || 'MXN'
  if (userCur === props.displayCurrency) return val
  if (userCur === 'MXN' && props.displayCurrency === 'USD') return val / exchangeRate.value
  if (userCur === 'USD' && props.displayCurrency === 'MXN') return val * exchangeRate.value
  return val
}

const currentMoney = computed(() => {
  const raw = freeMoney.value + totalFundsAmount.value
  return convertToDisplay(raw)
})

const withdrawnMoney = computed(() => {
  const now = new Date().getTime()
  const msPerDay = 24 * 60 * 60 * 1000
  const tf = timeFrames.find(t => t.id === activeTimeFrame.value)
  let startDate = tf?.days === 0 ? 0 : now - (tf?.days || 30) * msPerDay

  const raw = transactions.value
    .filter(t => t.type === 'expense' && new Date(t.date).getTime() >= startDate)
    .reduce((sum, t) => sum + parseFloat(t.amount), 0)
  return convertToDisplay(raw)
})

const totalValueFormatted = computed(() => {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: props.displayCurrency 
  }).format(currentMoney.value)
})

const chartOption = computed(() => {
  const dineroActual = currentMoney.value
  const dineroSacado = withdrawnMoney.value

  return {
    tooltip: {
      ...commonTooltip,
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
      bottom: '0%',
      left: 'center',
      textStyle: { color: CHART_COLORS.textSecondary },
      icon: 'circle',
      itemGap: 24,
    },
    series: [
      {
        name: 'Dinero',
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
            fontSize: 14,
            fontWeight: 'bold',
            color: CHART_COLORS.textPrimary,
            fontFamily: 'Inter, Geist, sans-serif'
          }
        },
        labelLine: { show: false },
        data: [
          { value: dineroActual, name: 'Dinero Actual', itemStyle: { ...getTranslucentStyle(CHART_COLORS.positive) } },
          { value: dineroSacado, name: 'Dinero Sacado', itemStyle: { ...getTranslucentStyle(CHART_COLORS.negative) } }
        ]
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border/50 bg-[#111111] flex flex-col rounded-[20px] shadow-none p-2 sm:p-4">
    <CardHeader class="pb-2">
      <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <CardTitle class="text-base font-normal text-[#a1a1aa]">Dinero Actual vs Sacado</CardTitle>
          <div class="mt-1 flex items-baseline gap-2">
            <span class="text-3xl font-bold text-white tracking-tight">{{ totalValueFormatted }}</span>
          </div>
          <CardDescription class="text-[#6b7280]">Balance en cuenta vs Gastos/Retiros</CardDescription>
        </div>
        
        <div class="flex items-center gap-2 bg-black/40 p-1 rounded-lg border border-white/5">
          <button
            v-for="tf in timeFrames"
            :key="tf.id"
            @click="activeTimeFrame = tf.id"
            :class="[
              'px-3 py-1 text-xs font-medium rounded-md transition-colors',
              activeTimeFrame === tf.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
            ]"
          >
            {{ tf.label }}
          </button>
        </div>
      </div>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-0 mt-4 flex items-center justify-center">
      <div v-if="isLoading" class="text-[#6b7280] text-sm animate-pulse">
        Cargando datos...
      </div>
      <div v-else-if="currentMoney === 0 && withdrawnMoney === 0" class="text-[#6b7280] text-sm">
        No hay datos suficientes
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
