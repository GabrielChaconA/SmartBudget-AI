<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
import NetWorthCard from '@/components/home/NetWorthCard.vue'
import SummaryCards from '@/components/home/SummaryCards.vue'
import InvestmentsCard from '@/components/home/InvestmentsCard.vue'
import UpcomingPayments from '@/components/home/UpcomingPayments.vue'
import AiInsightCard from '@/components/home/AiInsightCard.vue'
import { useUser } from '@/composables/useUser'
import { Eye, EyeOff } from '@lucide/vue'
import { Button } from '@/components/ui/button'

const { user, isBalancesVisible, toggleBalances } = useUser()
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            Good morning, {{ user?.name ? user.name.split(" ")[0] : 'Guest' }}
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            Here's a clear look at your finances today.
          </p>
        </div>
        <Button variant="ghost" size="icon" @click="toggleBalances" class="text-muted-foreground hover:text-foreground">
          <Eye v-if="isBalancesVisible" class="size-5" />
          <EyeOff v-else class="size-5" />
        </Button>
      </div>

      <NetWorthCard />
      
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div class="lg:col-span-3">
          <SummaryCards />
        </div>
        <div class="lg:col-span-1">
          <InvestmentsCard />
        </div>
      </div>

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
