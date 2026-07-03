<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
import AnalyticsFilters from '@/components/analytics/AnalyticsFilters.vue'
import TotalWealthAllocation from '@/components/analytics/TotalWealthAllocation.vue'
import FundsVsFreeAllocation from '@/components/analytics/FundsVsFreeAllocation.vue'
import InvestmentPerformanceChart from '@/components/analytics/InvestmentPerformanceChart.vue'
import MonthlySubscriptionsChart from '@/components/analytics/MonthlySubscriptionsChart.vue'
import AllFundsAllocation from '@/components/analytics/AllFundsAllocation.vue'
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-[1200px] flex-col gap-6 pb-12">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-foreground">
          Analytics
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          A complete business-intelligence view of your finances.
        </p>
      </div>

      <!-- Filters -->
      <AnalyticsFilters />

      <!-- Gráficas Pequeñas (Máximo 2 juntas en PC) -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TotalWealthAllocation />
        <FundsVsFreeAllocation />
      </div>

      <!-- Gráficas Grandes (1 por fila abajo) -->
      <div class="grid grid-cols-1 gap-6">
        <AllFundsAllocation />
      </div>

      <div class="grid grid-cols-1 gap-6">
        <InvestmentPerformanceChart />
      </div>

      <div class="grid grid-cols-1 gap-6">
        <MonthlySubscriptionsChart />
      </div>
    </div>
  </DashboardLayout>
</template>
