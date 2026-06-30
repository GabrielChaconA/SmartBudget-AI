<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
import NetWorthCard from '@/components/home/NetWorthCard.vue'
import SummaryCards from '@/components/home/SummaryCards.vue'
import UpcomingPayments from '@/components/home/UpcomingPayments.vue'
import AiInsightCard from '@/components/home/AiInsightCard.vue'
import { user } from '@/lib/data'
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-foreground">
          Good morning, {{ user.name.split(" ")[0] }}
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          Here's a clear look at your finances today.
        </p>
      </div>

      <NetWorthCard />
      <SummaryCards />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div class="lg:col-span-2">
          <AiInsightCard />
        </div>
        <div class="lg:col-span-1">
          <UpcomingPayments />
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
