<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { TrendingUp, TrendingDown, Layers, Building2, Bitcoin, Dices, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle, Plus, Eye, EyeOff, Edit2, Bell } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { portfolioPerformance, formatCurrency, investmentHoldings, type InvestmentCategory, type InvestmentHolding } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import { useInvestments } from '@/composables/useInvestments'
import { useRouter } from 'vue-router'
import AssetLogo from '@/components/AssetLogo.vue'
import AddInvestmentModal from '@/components/AddInvestmentModal.vue'
import EditInvestmentModal from '@/components/EditInvestmentModal.vue'
import InvestmentAlertModal from '@/components/InvestmentAlertModal.vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])

const categoryIcons: Record<string, any> = {
  all: Layers,
  etfs: Layers,
  stocks: Building2,
  crypto: Bitcoin,
  bets: Dices,
}

const { user, isBalancesVisible, toggleBalances, isItemVisible, toggleItemVisibility } = useUser()
const { activeCategories, activeHoldings, totalPortfolioValue, isLoading, isError, lastUpdate, exchangeRate, fetchData: _fetchData } = useInvestments()
const router = useRouter()

const isAddModalOpen = ref(false)
const isEditModalOpen = ref(false)
const isAlertModalOpen = ref(false)
const selectedInvestmentToEdit = ref<any>(null)
const selectedHoldingForAlert = ref<any>(null)

const displayCurrency = ref(user.value?.currency || 'MXN')

watch(() => user.value?.currency, (newVal) => {
  if (newVal && !displayCurrency.value) displayCurrency.value = newVal
})

const toggleCurrency = () => {
  displayCurrency.value = displayCurrency.value === 'MXN' ? 'USD' : 'MXN'
}

const openEditModal = (holding: any) => {
  const originalInvestment = user.value?.investments?.find((i: any) => i.id === holding.id)
  if (originalInvestment) {
    selectedInvestmentToEdit.value = originalInvestment
    isEditModalOpen.value = true
  }
}

const openAlertModal = (holding: any) => {
  selectedHoldingForAlert.value = holding
  isAlertModalOpen.value = true
}

const activeCat = ref('all')
const holdings = computed(() => {
  if (activeCat.value === 'all') {
    return [
      ...(activeHoldings.value.etfs || []),
      ...(activeHoldings.value.stocks || []),
      ...(activeHoldings.value.crypto || []),
      ...(activeHoldings.value.bets || [])
    ]
  }
  return activeHoldings.value[activeCat.value] ?? []
})

const getDisplayValue = (val: number) => {
  if (!val) return 0;
  const userCurrency = user.value?.currency || 'MXN';
  if (userCurrency === 'MXN' && displayCurrency.value === 'USD') return val / exchangeRate.value;
  if (userCurrency === 'USD' && displayCurrency.value === 'MXN') return val * exchangeRate.value;
  return val;
}

const fetchData = () => _fetchData(user.value)

onMounted(() => {
  fetchData()
})

watch(() => user.value?.investments, () => {
  fetchData()
}, { deep: true })

import { CHART_COLORS, commonTooltip, commonGrid, commonXAxis, commonYAxis } from '@/lib/chartTheme'

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...commonTooltip,
    trigger: 'axis',
    formatter: (params: any) => {
      const v = getDisplayValue(params[0].value)
      const date = params[0].name
      return `<span style="color:${CHART_COLORS.textSecondary}">${date}</span><br/><span style="color:${CHART_COLORS.textPrimary};font-weight:700;font-size:14px;">$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)} ${displayCurrency.value}</span>`
    }
  },
  grid: { 
    ...commonGrid,
    left: 45, 
    right: 16, 
    top: 16, 
    bottom: 16 
  },
  xAxis: {
    ...commonXAxis,
    type: 'category',
    data: portfolioPerformance.map(item => item.month),
    boundaryGap: false
  },
  yAxis: {
    ...commonYAxis,
    type: 'value',
    axisLabel: {
      ...commonYAxis.axisLabel,
      formatter: (v: number) => `$${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(getDisplayValue(v))}`
    }
  },
  series: [
    {
      data: portfolioPerformance.map(item => item.value),
      type: 'line',
      smooth: true,
      showSymbol: false,
      itemStyle: { color: CHART_COLORS.primary },
      lineStyle: { width: 3 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{
              offset: 0, color: 'rgba(29, 161, 242, 0.4)'
          }, {
              offset: 1, color: 'rgba(29, 161, 242, 0)'
          }]
        }
      },
      animationDuration: 1000,
      animationEasing: 'cubicOut'
    }
  ]
}))
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-6xl">
      <header class="pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            Investments
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            Track the performance of your ETFs, companies, crypto and relevant bets.
          </p>
        </div>
        <div class="flex flex-col items-end gap-2">
          <div class="flex items-center gap-3">
            <span v-if="lastUpdate" class="text-xs text-muted-foreground">
              Última actualización: {{ lastUpdate.toLocaleTimeString() }}
            </span>
            <button 
              @click="toggleCurrency"
              class="flex items-center justify-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-primary transition-colors hover:bg-primary/20"
            >
              <RefreshCw class="size-3" />
              {{ displayCurrency }}
            </button>
            <Button variant="outline" size="sm" @click="fetchData" :disabled="isLoading">
              <RefreshCw class="size-4 mr-2" :class="{ 'animate-spin': isLoading }" />
              Actualizar
            </Button>
          </div>
          <span v-if="isError" class="text-xs text-destructive flex items-center gap-1">
            <AlertCircle class="size-3" /> Error al obtener algunos datos
          </span>
        </div>
      </header>

      <!-- Top summary -->
      <div class="grid gap-4 lg:grid-cols-3">
        <Card class="lg:col-span-2 border-border">
          <CardHeader class="flex-row items-start justify-between space-y-0">
            <div>
              <CardDescription>{{ activeCat === 'all' ? 'Total portfolio value' : activeCategories.find(c => c.id === activeCat)?.label + ' Value' }}</CardDescription>
              <CardTitle class="text-3xl flex items-center gap-2">
                <span v-if="isItemVisible('invest_total')">{{ formatCurrency(getDisplayValue(activeCategories.find(c => c.id === activeCat)?.value || 0), displayCurrency) }}</span>
                <span v-else>••••••</span>
                <Button variant="ghost" size="icon" @click.stop="toggleItemVisibility('invest_total')" class="h-8 w-8 text-muted-foreground hover:text-foreground">
                  <Eye v-if="isItemVisible('invest_total')" class="size-4" />
                  <EyeOff v-else class="size-4" />
                </Button>
              </CardTitle>
              <div class="mt-2 flex items-center gap-3">
                <span :class="[
                  'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                  (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) >= 0 ? 'text-primary' : 'text-destructive'
                ]">
                  <ArrowUpRight v-if="(activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) >= 0" class="size-3.5" />
                  <ArrowDownRight v-else class="size-3.5" />
                  {{ (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0) > 0 ? '+' : '' }}{{ (activeCategories.find(c => c.id === activeCat)?.returnPercent || 0).toFixed(1) }}%
                </span>
                <span class="text-sm text-muted-foreground">today</span>
              </div>
            </div>
            <span class="flex size-11 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <TrendingUp class="size-5" />
            </span>
          </CardHeader>
          <CardContent>
            <div class="h-[200px] w-full">
              <v-chart class="h-full w-full" :option="chartOption" autoresize />
            </div>
          </CardContent>
        </Card>

        <Card 
          :class="[
            'border-border transition-colors',
            activeCat !== 'all' ? 'cursor-pointer hover:border-primary/50 group' : ''
          ]" 
          @click="activeCat !== 'all' ? isAddModalOpen = true : null"
        >
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle class="text-base flex items-center gap-2">
                Summary
                <Button variant="ghost" size="icon" @click.stop="toggleItemVisibility('invest_summary')" class="h-6 w-6 text-muted-foreground hover:text-foreground">
                  <Eye v-if="isItemVisible('invest_summary')" class="size-3" />
                  <EyeOff v-else class="size-3" />
                </Button>
              </CardTitle>
              <div v-if="activeCat !== 'all'" class="flex size-6 items-center justify-center rounded bg-primary text-primary-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                <Plus class="size-4" />
              </div>
            </div>
            <CardDescription>Portfolio breakdown.{{ activeCat !== 'all' ? ' Click to add.' : '' }}</CardDescription>
          </CardHeader>
          <CardContent class="flex flex-col gap-3">
            <template v-if="activeCat === 'all'">
              <div v-for="cat in activeCategories.filter(c => c.id !== 'all' && c.value > 0)" :key="cat.id" class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground flex items-center gap-2">
                  <component :is="categoryIcons[cat.id]" class="size-4" />
                  {{ cat.label }}
                </span>
                <span class="font-semibold tabular-nums text-foreground">
                  <span v-if="isItemVisible('invest_summary')">{{ formatCurrency(getDisplayValue(cat.value), displayCurrency) }}</span>
                  <span v-else>••••••</span>
                </span>
              </div>
              
              <div v-if="activeCategories.filter(c => c.id !== 'all' && c.value > 0).length === 0" class="text-sm text-muted-foreground text-center py-2">
                No active investments
              </div>
            </template>
            <template v-else>
              <div 
                v-for="h in holdings" 
                :key="h.id" 
                class="flex items-center justify-between group cursor-pointer hover:bg-accent/50 p-1 -mx-1 rounded-md transition-colors"
                @click.stop="openEditModal(h)"
              >
                <span class="text-sm text-muted-foreground flex items-center gap-2">
                  <div class="flex size-5 items-center justify-center rounded overflow-hidden bg-accent">
                    <AssetLogo :symbol="h.ticker" :fallback-icon="h.returnPercent >= 0 ? TrendingUp : TrendingDown" />
                  </div>
                  {{ h.name }}
                </span>
                <span class="font-semibold tabular-nums text-foreground flex items-center gap-2">
                  <span v-if="isItemVisible('invest_summary')">{{ formatCurrency(getDisplayValue(h.value), displayCurrency) }}</span>
                  <span v-else>••••••</span>
                  <Bell class="size-4 opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-primary transition-all" @click.stop="openAlertModal(h)" />
                  <Edit2 class="size-4 opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-primary transition-all" @click.stop="openEditModal(h)" />
                </span>
              </div>
              
              <div v-if="holdings.length === 0" class="text-sm text-muted-foreground text-center py-2">
                No active investments in this category
              </div>
            </template>
            
            <div class="h-px w-full bg-border my-1"></div>
            
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-foreground">Total</span>
              <span class="font-bold tabular-nums text-primary">
                <span v-if="isItemVisible('invest_summary')">
                  {{ formatCurrency(getDisplayValue(activeCat === 'all' ? totalPortfolioValue : (activeCategories.find(c => c.id === activeCat)?.value || 0)), displayCurrency) }}
                </span>
                <span v-else>••••••</span>
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Category cards -->
      <section class="mt-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          By category
        </h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <button
            v-for="cat in activeCategories"
            :key="cat.id"
            type="button"
            @click="activeCat = cat.id"
            :class="[
              'rounded-xl border p-4 text-left transition-colors',
              activeCat === cat.id ? 'border-primary bg-accent' : 'border-border bg-card hover:border-primary/50'
            ]"
          >
            <div class="flex items-center justify-between">
              <span :class="[
                'flex size-10 items-center justify-center rounded-xl',
                activeCat === cat.id ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'
              ]">
                <component :is="categoryIcons[cat.id]" class="size-5" />
              </span>
              <span :class="[
                'inline-flex items-center gap-0.5 text-sm font-medium tabular-nums',
                cat.returnPercent >= 0 ? 'text-primary' : 'text-destructive'
              ]">
                <ArrowUpRight v-if="cat.returnPercent >= 0" class="size-3.5" />
                <ArrowDownRight v-else class="size-3.5" />
                {{ cat.returnPercent > 0 ? '+' : '' }}{{ cat.returnPercent.toFixed(1) }}%
              </span>
            </div>
            <p class="mt-3 text-sm text-muted-foreground">{{ cat.label }}</p>
            <p class="text-lg font-semibold text-foreground flex items-center justify-between">
              <span>
                <span v-if="isItemVisible('invest_cat_' + cat.id)">{{ formatCurrency(getDisplayValue(cat.value), displayCurrency) }}</span>
                <span v-else>••••••</span>
              </span>
              <button @click.stop="toggleItemVisibility('invest_cat_' + cat.id)" class="text-muted-foreground hover:text-foreground">
                <Eye v-if="isItemVisible('invest_cat_' + cat.id)" class="size-4" />
                <EyeOff v-else class="size-4" />
              </button>
            </p>
          </button>
        </div>
      </section>
    </div>
    
    <AddInvestmentModal v-model:open="isAddModalOpen" :initial-category="activeCat !== 'all' ? activeCat : undefined" :default-currency="displayCurrency" />
    <EditInvestmentModal v-model:open="isEditModalOpen" :investment="selectedInvestmentToEdit" :default-currency="displayCurrency" />
    <InvestmentAlertModal v-model:isOpen="isAlertModalOpen" :holding="selectedHoldingForAlert" />
  </DashboardLayout>
</template>
