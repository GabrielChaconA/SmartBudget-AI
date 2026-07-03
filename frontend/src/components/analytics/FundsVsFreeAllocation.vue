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

const { freeMoney, user } = useUser()

const chartOption = computed(() => {
  const freeItemStyle = { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: '#22c55e'}, {offset: 1, color: '#064e3b'}] } }

  const fundsData = (user.value?.funds || []).map((f: any, idx: number) => {
    // Generate different solid shades of green for funds based on index
    const shades = [['#4ade80', '#166534'], ['#22c55e', '#064e3b'], ['#16a34a', '#052e16'], ['#15803d', '#052e16'], ['#166534', '#022c22'], ['#064e3b', '#022c22']]
    const s = shades[idx % shades.length]
    
    return {
      value: parseFloat(f.balance),
      name: f.name || 'Caja',
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: s[0]}, {offset: 1, color: s[1]}] } }
    }
  }).filter((item: any) => item.value > 0)

  const data = [
    { value: freeMoney.value, name: 'Dinero Libre', itemStyle: freeItemStyle },
    ...fundsData
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
      type: 'scroll',
      bottom: '2%',
      left: 'center',
      textStyle: { color: '#a1a1aa' } // text-muted-foreground
    },
    series: [
      {
        name: 'Dinero Disponible',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 0,
          borderColor: '#09090b',
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
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
      <CardTitle class="text-base">Dinero Disponible</CardTitle>
      <CardDescription>Cajas (Funds) vs Dinero Libre</CardDescription>
    </CardHeader>
    <CardContent class="h-[300px] w-full p-4 flex items-center justify-center">
      <div v-if="freeMoney === 0 && (user?.funds || []).length === 0" class="text-muted-foreground text-sm">
        No hay datos suficientes
      </div>
      <VChart v-else :option="chartOption" autoresize class="w-full h-full" />
    </CardContent>
  </Card>
</template>
