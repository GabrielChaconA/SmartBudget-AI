<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useUser } from '@/composables/useUser'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TooltipComponent, LegendComponent, PieChart, CanvasRenderer])

const { freeMoney, totalSubscriptionsAmount, totalInvestmentsAmount, user } = useUser()

const chartOption = computed(() => {
  const free = freeMoney.value
  const subs = totalSubscriptionsAmount.value
  const inv = totalInvestmentsAmount.value

  const data = [
    { 
      value: free, 
      name: 'Dinero Libre', 
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: '#86efac'}, {offset: 1, color: '#166534'}] } } 
    },
    { 
      value: subs, 
      name: 'Suscripciones (Mes)', 
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: '#22c55e'}, {offset: 1, color: '#064e3b'}] } } 
    },
    { 
      value: inv, 
      name: 'Inversiones', 
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: '#15803d'}, {offset: 1, color: '#052e16'}] } } 
    }
  ].filter(item => item.value > 0)

  return {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: user.value?.currency || 'MXN'
        }).format(params.value)
        return `${params.name}: <br/><b>${val}</b> (${params.percent}%)`
      }
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: { color: '#a1a1aa' } // text-muted-foreground
    },
    series: [
      {
        name: 'Distribución',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#09090b', // match background to create gaps
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#f4f4f5'
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
  <Card class="border-border flex flex-col">
    <CardHeader class="pb-2">
      <CardTitle class="text-base">Distribución Global</CardTitle>
      <CardDescription>Dinero libre vs Suscripciones vs Inversiones</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-4 flex items-center justify-center">
      <div v-if="freeMoney === 0 && totalSubscriptionsAmount === 0 && totalInvestmentsAmount === 0" class="text-muted-foreground text-sm">
        No hay datos suficientes
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
