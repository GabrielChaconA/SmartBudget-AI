<script setup lang="ts">
import { ref, watch, provide } from 'vue'
import { RefreshCw } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import AnalyticsFilters from '@/components/analytics/AnalyticsFilters.vue'
import TotalWealthAllocation from '@/components/analytics/TotalWealthAllocation.vue'
import FundsVsFreeAllocation from '@/components/analytics/FundsVsFreeAllocation.vue'
import InvestmentPerformanceChart from '@/components/analytics/InvestmentPerformanceChart.vue'
import MonthlySubscriptionsChart from '@/components/analytics/MonthlySubscriptionsChart.vue'
import AllFundsAllocation from '@/components/analytics/AllFundsAllocation.vue'
import { useUser } from '@/composables/useUser'

const { user } = useUser()

const displayCurrency = ref(user.value?.currency || 'MXN')
watch(() => user.value?.currency, (newVal) => {
  if (newVal && !displayCurrency.value) displayCurrency.value = newVal
})

const toggleCurrency = () => {
  displayCurrency.value = displayCurrency.value === 'MXN' ? 'USD' : 'MXN'
}

provide('displayCurrency', displayCurrency)
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-[1200px] flex-col gap-6 pb-12">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            Analytics
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            A complete business-intelligence view of your finances.
          </p>
        </div>
        
        <button 
          @click="toggleCurrency"
          class="flex items-center justify-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-primary transition-colors hover:bg-primary/20"
        >
          <RefreshCw class="size-3" />
          {{ displayCurrency }}
        </button>
      </div>

      <!-- Filters -->
      <AnalyticsFilters />

      <!-- Gráficas Pequeñas (Máximo 2 juntas en PC) -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TotalWealthAllocation :key="displayCurrency" />
        <FundsVsFreeAllocation :key="displayCurrency" />
      </div>

      <!-- Gráficas Grandes (1 por fila abajo) -->
      <div class="grid grid-cols-1 gap-6">
        <AllFundsAllocation :key="displayCurrency" />
      </div>

      <div class="grid grid-cols-1 gap-6">
        <InvestmentPerformanceChart />
      </div>

      <div class="grid grid-cols-1 gap-6">
        <MonthlySubscriptionsChart :key="displayCurrency" />
      </div>
    </div>
  </DashboardLayout>
</template>
