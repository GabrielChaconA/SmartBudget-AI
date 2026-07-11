<script setup lang="ts">
import { ref, watch } from 'vue'
import { RefreshCw } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import CurrentVsWithdrawnChart from '@/components/analytics/CurrentVsWithdrawnChart.vue'
import FundsVsFreeAllocation from '@/components/analytics/FundsVsFreeAllocation.vue'
import InvestmentPerformanceChart from '@/components/analytics/InvestmentPerformanceChart.vue'
import MonthlySubscriptionsChart from '@/components/analytics/MonthlySubscriptionsChart.vue'
import { useUser } from '@/composables/useUser'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const { user } = useUser()

const displayCurrency = ref(user.value?.currency || 'MXN')
watch(() => user.value?.currency, (newVal) => {
  if (newVal && !displayCurrency.value) displayCurrency.value = newVal
})

const toggleCurrency = () => {
  displayCurrency.value = displayCurrency.value === 'MXN' ? 'USD' : 'MXN'
}

</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-[1200px] flex-col gap-6 pb-12">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            {{ $t('analytics.title') }}
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            {{ $t('analytics.subtitle') }}
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



      <!-- Gráficas Pequeñas (Máximo 2 juntas en PC) -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CurrentVsWithdrawnChart :display-currency="displayCurrency" />
        <FundsVsFreeAllocation :display-currency="displayCurrency" />
      </div>



      <div class="grid grid-cols-1 gap-6">
        <InvestmentPerformanceChart :display-currency="displayCurrency" />
      </div>

      <div class="grid grid-cols-1 gap-6">
        <MonthlySubscriptionsChart :display-currency="displayCurrency" />
      </div>
    </div>
  </DashboardLayout>
</template>
