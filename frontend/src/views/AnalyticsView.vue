<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
import AnalyticsFilters from '@/components/analytics/AnalyticsFilters.vue'
import NetWorthChart from '@/components/analytics/NetWorthChart.vue'
import IncomeExpenseChart from '@/components/analytics/IncomeExpenseChart.vue'
import BudgetAllocation from '@/components/analytics/BudgetAllocation.vue'
import TopSpendingCategories from '@/components/analytics/TopSpendingCategories.vue'
import InvestmentAllocation from '@/components/analytics/InvestmentAllocation.vue'
import MonthlySavingsRate from '@/components/analytics/MonthlySavingsRate.vue'
import RecentTransactions from '@/components/analytics/RecentTransactions.vue'
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

      <!-- Row 1: Net Worth & Income vs Expenses -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <NetWorthChart />
        <IncomeExpenseChart />
      </div>

      <!-- Row 2: Budget Allocation & Top Spending Categories -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <BudgetAllocation />
        <TopSpendingCategories />
      </div>

      <!-- Row 3: Investment Allocation & Monthly Savings Rate -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <InvestmentAllocation />
        <MonthlySavingsRate />
      </div>

      <!-- Row 4: Recent Transactions -->
      <div class="grid grid-cols-1">
        <RecentTransactions />
      </div>
    </div>
  </DashboardLayout>
</template>
