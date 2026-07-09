<script setup lang="ts">
import { computed, ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useInvestments } from '@/composables/useInvestments'
import { useUser } from '@/composables/useUser'
import { useChartTheme } from '@/lib/chartTheme'

echarts.use([TooltipComponent, GridComponent, LegendComponent, LineChart, CanvasRenderer])

const { activeHoldings, exchangeRate } = useInvestments()
const { user } = useUser()
const props = defineProps<{
  displayCurrency: string
}>()

const categories = [
  { id: 'stocks', label: 'Empresas', color: '#3b82f6' },
  { id: 'etfs', label: 'ETFs', color: '#10b981' },
  { id: 'crypto', label: 'Criptos', color: '#f59e0b' }
]

const timeFrames = [
  { id: '7D', label: '7D' },
  { id: '1M', label: '1M' },
  { id: '1Y', label: '1A' },
  { id: 'ALL', label: 'Todo' }
]

const activeCat = ref('all')
const activeTimeFrame = ref('1Y')

const getStartDate = (tfId: string, now: number, msPerDay: number) => {
  const today = new Date()
  switch (tfId) {
    case '7D': return now - 7 * msPerDay
    case '1M': return now - 30 * msPerDay
    case '1Y': return new Date(today.getFullYear(), 0, 1).getTime() // January 1st of current year
    case 'ALL': return 0 // will be calculated from oldest holding
    default: return now - 365 * msPerDay
  }
}

const getHoldingValueAt = (h: any, t: number, currentNow: number, displayCur: string, exRate: number) => {
  const msPerDay = 24 * 60 * 60 * 1000;
  const createdTime = h.created_at ? new Date(h.created_at).getTime() : currentNow;
  if (t < createdTime) return 0;
  
  let origVal = h.originalValue || 0;
  if (h.originalCurrency === 'USD' && displayCur === 'MXN') origVal *= exRate;
  if (h.originalCurrency === 'MXN' && displayCur === 'USD') origVal /= exRate;
  
  let currVal = h.value || 0;
  const userCur = user.value?.currency || 'MXN';
  if (userCur === 'MXN' && displayCur === 'USD') currVal /= exRate;
  if (userCur === 'USD' && displayCur === 'MXN') currVal *= exRate;

  if (currentNow <= createdTime) return currVal;
  
  const ratio = (t - createdTime) / (currentNow - createdTime);
  const clampedRatio = Math.max(0, Math.min(1, ratio));
  
  return origVal + (currVal - origVal) * clampedRatio;
}

const { CHART_COLORS, commonTooltip, commonGrid, commonYAxis } = useChartTheme()
const chartOption = computed(() => {
  const now = new Date().getTime()
  const msPerDay = 24 * 60 * 60 * 1000
  
  let startDate = getStartDate(activeTimeFrame.value, now, msPerDay)
  
  if (activeTimeFrame.value === 'ALL') {
    let oldest = now
    if (activeCat.value === 'all') {
      categories.forEach(cat => {
        const holdings = activeHoldings.value[cat.id] || []
        holdings.forEach((h: any) => {
          const cTime = h.created_at ? new Date(h.created_at).getTime() : now
          if (cTime < oldest) oldest = cTime
        })
      })
    } else {
      const holdings = activeHoldings.value[activeCat.value] || []
      holdings.forEach((h: any) => {
        const cTime = h.created_at ? new Date(h.created_at).getTime() : now
        if (cTime < oldest) oldest = cTime
      })
    }
    startDate = oldest - msPerDay
  }

  const seriesData: any[] = []
  
  if (activeCat.value === 'all') {
    categories.forEach(cat => {
      const holdings = activeHoldings.value[cat.id] || []
      
      const timestamps = new Set<number>()
      timestamps.add(startDate)
      timestamps.add(now)
      
      holdings.forEach((h: any) => {
        const cTime = h.created_at ? new Date(h.created_at).getTime() : now
        if (cTime > startDate && cTime < now) {
          // Add a point 1ms before creation so the line stays at 0 then jumps
          timestamps.add(cTime - 1)
          timestamps.add(cTime)
        }
      })
      
      const sortedTimes = Array.from(timestamps).sort((a, b) => a - b)
      
      const dataPoints = sortedTimes.map(t => {
        let totalVal = 0
        holdings.forEach((h: any) => {
          totalVal += getHoldingValueAt(h, t, now, props.displayCurrency, exchangeRate.value)
        })
        return [t, totalVal]
      })
      
      seriesData.push({
        name: cat.label,
        type: 'line',
        smooth: false,
        showSymbol: false,
        data: dataPoints,
        itemStyle: { color: cat.color },
        lineStyle: { width: 2 },
        areaStyle: {
          opacity: 0.2,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: cat.color },
            { offset: 1, color: 'rgba(0,0,0,0)' }
          ])
        },
        animationDuration: 800
      })
    })
  } else {
    // Desglose de la categoría seleccionada
    const holdings = activeHoldings.value[activeCat.value] || []
    
    holdings.forEach((h: any, index: number) => {
      const timestamps = new Set<number>()
      timestamps.add(startDate)
      timestamps.add(now)
      
      const cTime = h.created_at ? new Date(h.created_at).getTime() : now
      if (cTime > startDate && cTime < now) {
        // Add a point 1ms before creation so the line stays at 0 then jumps
        timestamps.add(cTime - 1)
        timestamps.add(cTime)
      }
      
      const sortedTimes = Array.from(timestamps).sort((a, b) => a - b)
      const dataPoints = sortedTimes.map(t => {
        return [t, getHoldingValueAt(h, t, now, props.displayCurrency, exchangeRate.value)]
      })
      
      const color = CHART_COLORS.distinctColors[index % CHART_COLORS.distinctColors.length]
      
      seriesData.push({
        name: h.ticker || h.name,
        type: 'line',
        smooth: false,
        showSymbol: false,
        data: dataPoints,
        itemStyle: { color },
        lineStyle: { width: 2 },
        areaStyle: {
          opacity: 0.2,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color },
            { offset: 1, color: 'rgba(0,0,0,0)' }
          ])
        },
        animationDuration: 800
      })
    })
  }

  return {
    tooltip: {
      ...commonTooltip,
      trigger: 'axis',
      formatter: (params: any) => {
        const date = new Date(params[0].value[0]).toLocaleDateString()
        let html = `<span style="color:${CHART_COLORS.textSecondary}">${date}</span><br/>`
        // Sort tooltip items by value descending
        const sortedParams = [...params].sort((a, b) => (b.value[1] || 0) - (a.value[1] || 0))
        sortedParams.forEach((p: any) => {
          if (p.value[1] === 0 && activeCat.value !== 'all') return; // Skip showing 0 if breakdown
          const val = new Intl.NumberFormat('en-US', { style: 'currency', currency: props.displayCurrency }).format(p.value[1])
          html += `<div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color}"></span>
            <span style="color:${CHART_COLORS.textSecondary}">${p.seriesName}:</span>
            <span style="color:${CHART_COLORS.textPrimary};font-weight:600">${val}</span>
          </div>`
        })
        return html
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
      type: 'time',
      splitLine: { show: false },
      axisLabel: { 
        color: CHART_COLORS.textSecondary,
        formatter: (val: number) => {
          const d = new Date(val)
          return activeTimeFrame.value === '7D' ? d.toLocaleDateString(undefined, { weekday: 'short' }) : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        }
      },
      axisLine: { lineStyle: { color: CHART_COLORS.gridLine } }
    },
    yAxis: {
      ...commonYAxis,
      type: 'value',
      splitLine: {
        show: true,
        lineStyle: { type: 'dashed', color: CHART_COLORS.gridLine }
      },
      axisLabel: { 
        ...commonYAxis.axisLabel, 
        formatter: (v: number) => `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)}` 
      }
    },
    series: seriesData
  }
})
</script>

<template>
  <Card class="border-border/50 bg-card flex flex-col rounded-[20px] shadow-none overflow-hidden pt-4 sm:pt-6">
    <CardHeader class="px-4 sm:px-6 pb-2">
      <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <CardTitle class="text-base font-normal text-muted-foreground">Rendimiento de Inversiones</CardTitle>
          <CardDescription class="text-muted-foreground mt-1">
            {{ activeCat === 'all' ? 'Evolución del valor por categoría' : 'Evolución de los activos individuales' }}
          </CardDescription>
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
      
      <div class="mt-4 flex flex-wrap gap-2">
        <button
          @click="activeCat = 'all'"
          :class="[
            'px-3 py-1 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5',
            activeCat === 'all' 
              ? 'bg-white/10 text-foreground border-white/20' 
              : 'bg-transparent text-muted-foreground border-border hover:border-white/20'
          ]"
        >
          Todos
        </button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="activeCat = cat.id"
          :class="[
            'px-3 py-1 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5',
            activeCat === cat.id
              ? 'bg-white/10 text-foreground border-white/20' 
              : 'bg-transparent text-muted-foreground border-border hover:border-white/20'
          ]"
        >
          <span class="size-2 rounded-full" :style="{ backgroundColor: cat.color, opacity: activeCat === cat.id ? 1 : 0.5 }"></span>
          {{ cat.label }}
        </button>
      </div>
    </CardHeader>
    <CardContent class="h-[350px] w-full p-0 mt-2">
      <VChart :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
