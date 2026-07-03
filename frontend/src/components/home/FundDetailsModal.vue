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
const allocAmount = ref(0)
const isSubmitting = ref(false)

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
  const diffWeeks = diffTime / (1000 * 3600 * 24 * 7)
  const diffMonths = diffTime / (1000 * 3600 * 24 * 30.44)
  const diffYears = diffTime / (1000 * 3600 * 24 * 365.25)
  
  statsData.value = {
    weekly: diffWeeks > 0 ? totalIncome / Math.max(1, diffWeeks) : totalIncome,
    monthly: diffMonths > 0 ? totalIncome / Math.max(1, diffMonths) : totalIncome,
    yearly: diffYears > 0 ? totalIncome / Math.max(1, diffYears) : totalIncome
  }
}

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    fetchAndProcessStats()
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

const handleSaveTotal = async () => {
  if (!props.fund || isOverLimit.value) return
  isSubmitting.value = true
  const success = await updateFund(props.fund.id, { balance: editBalance.value })
  if (success) {
    isEditingTotal.value = false
  }
  isSubmitting.value = false
}

const handleAddAllocation = async () => {
  if (!props.fund || !allocName.value || allocAmount.value <= 0) return
  isSubmitting.value = true
  const success = await allocateFund(props.fund.id, allocName.value, allocAmount.value)
  if (success) {
    isAddingAllocation.value = false
    allocName.value = ''
    allocAmount.value = 0
  }
  isSubmitting.value = false
}

const chartOption = computed(() => {
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['Weekly', 'Monthly', 'Yearly'],
      axisLabel: { color: '#a1a1aa' },
      axisLine: { lineStyle: { color: '#3f3f46' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#a1a1aa', formatter: (val: number) => `$${val}` },
      splitLine: { lineStyle: { color: '#27272a' } },
    },
    series: [
      {
        name: 'Average Income',
        type: 'bar',
        data: [
          Math.round(statsData.value.weekly),
          Math.round(statsData.value.monthly),
          Math.round(statsData.value.yearly)
        ],
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
})

</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[900px]">
      <DialogHeader>
        <DialogTitle>{{ fund?.name || 'Fund Details' }}</DialogTitle>
        <DialogDescription>
          Manage your fund balance, view internal allocations, and analyze average income.
        </DialogDescription>
      </DialogHeader>

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

            <div v-if="isAddingAllocation" class="flex items-end gap-2 mb-4 p-3 rounded-lg border border-border bg-muted/50">
              <div class="flex-1 space-y-1">
                <Label class="text-xs">Category</Label>
                <Input v-model="allocName" placeholder="e.g., Water" class="h-8 text-sm" />
              </div>
              <div class="w-24 space-y-1">
                <Label class="text-xs">Amount</Label>
                <Input v-model="allocAmount" type="number" class="h-8 text-sm" />
              </div>
              <Button size="sm" class="h-8" @click="handleAddAllocation" :disabled="isSubmitting || !allocName || allocAmount <= 0">Add</Button>
              <Button size="sm" variant="ghost" class="h-8 px-2" @click="isAddingAllocation = false">Cancel</Button>
            </div>

            <div class="space-y-3">
              <div v-for="(alloc, idx) in fund.allocations" :key="idx" class="flex items-center justify-between">
                <p class="text-sm font-medium">{{ alloc.category_name }}</p>
                <p class="text-sm font-semibold">{{ formatCurrency(alloc.amount, user?.currency) }}</p>
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
