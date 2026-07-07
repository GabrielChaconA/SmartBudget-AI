<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useUser } from '@/composables/useUser'
import { formatCurrency } from '@/lib/data'
import { Separator } from '@/components/ui/separator'
import { Pencil, Plus, Check, X } from '@lucide/vue'

import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TitleComponent, TooltipComponent, GridComponent, LegendComponent, BarChart, CanvasRenderer])

const props = defineProps<{
  open: boolean
  fund: any | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { updateFund, allocateFund, fetchIncomeStats, user, freeMoney } = useUser()

const isEditingTotal = ref(false)
const editBalance = ref(0)
const isAddingAllocation = ref(false)
const allocName = ref('')
const allocIcon = ref('')
const allocAmount = ref(0)
const isSubmitting = ref(false)
const errorMessage = ref('')
const editingAllocationIdx = ref<number | null>(null)
const editAllocAmount = ref<number>(0)

const statsData = ref({ weekly: 0, monthly: 0, yearly: 0 })

const fetchAndProcessStats = async () => {
  const data = await fetchIncomeStats()
  if (!data || data.length === 0) return
  let totalIncome = 0
  let minDate = new Date(data[0].date).getTime()
  let maxDate = new Date(data[0].date).getTime()
  
  data.forEach((tx: any) => {
    totalIncome += parseFloat(tx.amount)
    const txDate = new Date(tx.date).getTime()
    if (txDate < minDate) minDate = txDate
    if (txDate > maxDate) maxDate = txDate
  })
  
  const diffTime = Math.max(maxDate - minDate, 86400000) // at least 1 day
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  statsData.value = {
    weekly: (totalIncome / diffDays) * 7,
    monthly: (totalIncome / diffDays) * 30,
    yearly: (totalIncome / diffDays) * 365,
  }
}

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    fetchAndProcessStats()
    errorMessage.value = ''
  }
})

watch(() => props.fund, (newFund) => {
  if (newFund) {
    editBalance.value = parseFloat(newFund.balance)
  }
})

const maxAllowedBalance = computed(() => {
  if (!props.fund) return 0
  return parseFloat(props.fund.balance) + freeMoney.value
})

const isOverLimit = computed(() => {
  return editBalance.value > maxAllowedBalance.value
})

const totalAllocated = computed(() => {
  if (!props.fund?.allocations) return 0
  return props.fund.allocations.reduce((sum: number, a: any) => sum + parseFloat(a.amount), 0)
})

const fundFreeMoney = computed(() => {
  if (!props.fund) return 0
  return parseFloat(props.fund.balance) - totalAllocated.value
})

const handleSaveTotal = async () => {
  if (!props.fund) return
  errorMessage.value = ''
  if (isOverLimit.value) {
    errorMessage.value = 'El nuevo balance excede tu dinero libre disponible.'
    return
  }
  isSubmitting.value = true
  const success = await updateFund(props.fund.id, { balance: editBalance.value })
  if (success) {
    isEditingTotal.value = false
  } else {
    errorMessage.value = 'Hubo un error al actualizar la caja.'
  }
  isSubmitting.value = false
}

const handleAddAllocation = async () => {
  if (!props.fund || !allocName.value || allocAmount.value <= 0) return
  errorMessage.value = ''
  
  if (allocAmount.value > fundFreeMoney.value) {
    errorMessage.value = 'No tienes suficiente dinero libre en esta caja para esta operación.'
    return
  }

  isSubmitting.value = true
  const success = await allocateFund(props.fund.id, allocName.value, allocAmount.value, allocIcon.value)
  if (success) {
    isAddingAllocation.value = false
    allocName.value = ''
    allocIcon.value = ''
    allocAmount.value = 0
  } else {
    errorMessage.value = 'Hubo un error al guardar la asignación.'
  }
  isSubmitting.value = false
}

const handleUpdateAllocation = async (idx: number, alloc: any) => {
  if (editAllocAmount.value <= 0) return
  isSubmitting.value = true
  errorMessage.value = ''
  
  const totalAllocatedExceptThis = props.fund.allocations.reduce((sum: number, a: any, i: number) => {
    return i === idx ? sum : sum + parseFloat(a.amount)
  }, 0)
  
  const remaining = parseFloat(props.fund.balance) - totalAllocatedExceptThis
  
  if (editAllocAmount.value > remaining) {
    errorMessage.value = 'Monto supera el límite disponible en la caja.'
    isSubmitting.value = false
    return
  }

  const success = await allocateFund(props.fund.id, alloc.category_name, editAllocAmount.value, alloc.category_icon || '')
  isSubmitting.value = false
  if (success) {
    editingAllocationIdx.value = null
  } else {
    errorMessage.value = 'Error al actualizar sub-monto'
  }
}

const startEditAllocation = (idx: number, alloc: any) => {
  editingAllocationIdx.value = idx
  editAllocAmount.value = parseFloat(alloc.amount)
}

import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis, getTranslucentStyle } from '@/lib/chartTheme'

const chartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: { 
      ...commonTooltip,
      trigger: 'axis', 
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(params[0].value)
        return `<span style="color:${CHART_COLORS.textSecondary}">${params[0].name}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">${val}</span>`
      }
    },
    grid: { 
      ...commonGrid,
      left: 60,
      bottom: 30,
      top: 20
    },
    xAxis: {
      ...commonXAxis,
      type: 'category',
      data: ['Weekly', 'Monthly', 'Yearly'],
    },
    yAxis: {
      ...commonYAxis,
      type: 'value',
      axisLabel: { 
        ...commonYAxis.axisLabel, 
        formatter: (val: number) => `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(val)}` 
      },
    },
    series: [
      {
        name: 'Average Income',
        type: 'bar',
        barWidth: '40%',
        data: [
          Math.round(statsData.value.weekly),
          Math.round(statsData.value.monthly),
          Math.round(statsData.value.yearly)
        ],
        itemStyle: { 
          ...getTranslucentStyle(CHART_COLORS.primary), 
          borderRadius: [4, 4, 0, 0] 
        },
        emphasis: {
          itemStyle: { color: '#45b8ff' }
        },
        animationDuration: 400,
        animationEasing: 'cubicOut'
      }
    ]
  }
})


</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[900px]">
      <DialogHeader>
        <DialogTitle>{{ fund?.icon ? fund.icon + ' ' : '' }}{{ fund?.name || 'Fund Details' }}</DialogTitle>
        <DialogDescription>
          Manage your fund balance, view internal allocations, and analyze average income.
        </DialogDescription>
      </DialogHeader>

      <div v-if="errorMessage" class="mt-4 p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
        {{ errorMessage }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 py-4" v-if="fund">
        
        <!-- Left Column: Fund Management -->
        <div class="space-y-6">
          <div class="rounded-xl border border-border bg-card p-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-medium text-muted-foreground">Total Fund Balance</h3>
              <Button v-if="!isEditingTotal" variant="ghost" size="icon" class="size-6" @click="isEditingTotal = true">
                <Pencil class="size-3" />
              </Button>
            </div>
            
            <div v-if="isEditingTotal" class="flex flex-col gap-2">
              <div class="flex items-center gap-2">
                <Input type="number" v-model="editBalance" class="w-full" step="0.01" />
                <Button size="icon" variant="default" @click="handleSaveTotal" :disabled="isSubmitting || isOverLimit">
                  <Check class="size-4" />
                </Button>
                <Button size="icon" variant="ghost" @click="isEditingTotal = false">
                  <X class="size-4" />
                </Button>
              </div>
              <p v-if="isOverLimit" class="text-xs text-destructive">
                Cannot exceed free money limit ({{ formatCurrency(maxAllowedBalance, user?.currency) }})
              </p>
            </div>
            <div v-else>
              <p class="text-3xl font-bold">{{ formatCurrency(fund.balance, user?.currency) }}</p>
              <p class="mt-2 text-xs font-medium text-muted-foreground flex items-center gap-1">
                Disponible para agregar: <span class="text-foreground">{{ formatCurrency(freeMoney, user?.currency) }}</span> de dinero libre
              </p>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Sub-Amounts (Add to Total)</h3>
              <Button variant="outline" size="sm" class="h-7 gap-1" @click="isAddingAllocation = true" v-if="!isAddingAllocation">
                <Plus class="size-3" /> Add
              </Button>
            </div>

            <div v-if="isAddingAllocation" class="flex flex-col gap-2 mb-4 p-3 rounded-lg border border-border bg-muted/50">
              <div class="flex items-end gap-2">
                <div class="w-12 space-y-1">
                  <Label class="text-xs">Emoji</Label>
                  <Input v-model="allocIcon" placeholder="🛒" class="h-8 text-sm text-center px-1" maxlength="5" />
                </div>
                <div class="flex-1 space-y-1">
                  <Label class="text-xs">Category</Label>
                  <Input v-model="allocName" placeholder="e.g., Water" class="h-8 text-sm" />
                </div>
                <div class="w-32 space-y-1 relative">
                  <Label class="text-xs">Amount</Label>
                  <Input v-model="allocAmount" type="number" class="h-8 text-sm pr-10" />
                  <button class="absolute bottom-1 right-1 text-[10px] font-bold text-muted-foreground hover:text-foreground bg-muted px-1.5 py-0.5 rounded" @click="allocAmount = fundFreeMoney">MAX</button>
                </div>
                <Button size="sm" class="h-8" @click="handleAddAllocation" :disabled="isSubmitting || !allocName || allocAmount <= 0">Add</Button>
                <Button size="sm" variant="ghost" class="h-8 px-2" @click="isAddingAllocation = false">Cancel</Button>
              </div>
              <p class="text-[11px] text-muted-foreground text-right mt-1">Disponible en caja: <span class="font-bold text-foreground">{{ formatCurrency(fundFreeMoney, user?.currency) }}</span></p>
            </div>

            <div class="space-y-3">
              <div v-for="(alloc, idx) in fund.allocations" :key="idx" class="flex items-center justify-between group">
                <p class="text-sm font-medium"><span v-if="alloc.category_icon" class="mr-1">{{ alloc.category_icon }}</span>{{ alloc.category_name }}</p>
                
                <div v-if="editingAllocationIdx === idx" class="flex items-center gap-1">
                  <Input type="number" v-model="editAllocAmount" class="h-6 w-24 text-xs px-1 text-right" step="0.01" />
                  <Button size="icon" variant="ghost" class="h-6 w-6" @click="handleUpdateAllocation(idx, alloc)">
                    <Check class="size-4 text-green-500" />
                  </Button>
                  <Button size="icon" variant="ghost" class="h-6 w-6" @click="editingAllocationIdx = null">
                    <X class="size-4 text-muted-foreground" />
                  </Button>
                </div>
                <div v-else class="flex items-center gap-2 cursor-pointer hover:bg-muted/50 rounded px-1 -mx-1 transition-colors" @click="startEditAllocation(idx, alloc)">
                  <p class="text-sm font-semibold">{{ formatCurrency(Number(alloc.amount), user?.currency) }}</p>
                  <Pencil class="size-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <p v-if="!fund.allocations || fund.allocations.length === 0" class="text-sm text-muted-foreground text-center py-2">
                No sub-amounts added yet.
              </p>
              
              <Separator v-if="fund.allocations?.length > 0" class="my-2" />
              <div v-if="fund.allocations?.length > 0" class="flex justify-between items-center text-sm font-medium">
                <span class="text-muted-foreground">Sum of Sub-Amounts:</span>
                <span>{{ formatCurrency(totalAllocated, user?.currency) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Income Analytics -->
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold tracking-tight">Average Income</h3>
            <p class="text-sm text-muted-foreground">
              Based on your historical transactions, here is your average income to help you decide how much to allocate.
            </p>
          </div>
          
          <div class="h-[250px] w-full rounded-xl border border-border bg-card p-4">
            <VChart :option="chartOption" autoresize />
          </div>
        </div>

      </div>
    </DialogContent>
  </Dialog>
</template>
