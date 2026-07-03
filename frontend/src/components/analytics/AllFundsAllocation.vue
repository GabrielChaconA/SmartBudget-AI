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
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: user.value?.currency || 'MXN'
        }).format(params[0].value)
        return `${params[0].name}: <br/><b>${val}</b>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#a1a1aa' },
      axisLine: { lineStyle: { color: '#3f3f46' } }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: { type: 'dashed', color: '#27272a' }
      },
      axisLabel: { color: '#a1a1aa' }
    },
    series: [
      {
        name: 'Balance',
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#22c55e', // Solid green
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
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
      <CardTitle class="text-base">Balance de Cajas</CardTitle>
      <CardDescription>Dinero almacenado en cada caja individual</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-4">
      <div v-if="(user?.funds || []).length === 0" class="text-muted-foreground text-sm flex h-full items-center justify-center">
        No hay cajas creadas o con fondos
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
