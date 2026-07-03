<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TooltipComponent, GridComponent, BarChart, CanvasRenderer])

const { user } = useUser()

const chartOption = computed(() => {
  // Only active subscriptions
  const subs = (user.value?.subscriptions || [])
    .filter((s: any) => s.status !== 'inactive')
    .map((s: any) => {
      // Calculate monthly equivalent
      const monthlyCost = s.billing_cycle === 'yearly' ? parseFloat(s.amount) / 12 : parseFloat(s.amount)
      return { name: s.name, cost: monthlyCost }
    })
    .sort((a, b) => a.cost - b.cost) // Sort ascending for horizontal bar (largest at top)

  const names = subs.map(s => s.name)
  const values = subs.map(s => s.cost)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: user.value?.currency || 'MXN'
        }).format(params[0].value)
        return `${params[0].name}: <br/><b>${val}</b> / mes`
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      splitLine: {
        lineStyle: { type: 'dashed', color: '#27272a' }
      },
      axisLabel: { color: '#a1a1aa' }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#f4f4f5', width: 100, overflow: 'truncate' },
      axisLine: { lineStyle: { color: '#3f3f46' } }
    },
    series: [
      {
        name: 'Costo Mensual',
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#15803d', // Solid green
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          color: '#a1a1aa',
          formatter: (params: any) => `$${Math.round(params.value)}`
        }
      }
    ]
  }
})
</script>

<template>
  <Card class="border-border flex flex-col">
    <CardHeader class="pb-2">
      <CardTitle class="text-base">Gasto en Suscripciones</CardTitle>
      <CardDescription>Costo mensual por suscripción activa</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-4">
      <div v-if="(user?.subscriptions || []).length === 0" class="text-muted-foreground text-sm flex h-full items-center justify-center">
        No hay suscripciones activas
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
