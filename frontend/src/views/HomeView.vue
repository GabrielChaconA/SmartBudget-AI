<script setup lang="ts">
import { ref } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import NetWorthCard from '@/components/home/NetWorthCard.vue'
import SummaryCards from '@/components/home/SummaryCards.vue'
import InvestmentsCard from '@/components/home/InvestmentsCard.vue'
import UpcomingPayments from '@/components/home/UpcomingPayments.vue'
import AiInsightCard from '@/components/home/AiInsightCard.vue'
import AddMoneyModal from '@/components/home/AddMoneyModal.vue'
import { useUser } from '@/composables/useUser'
import { Eye, EyeOff, Plus } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { useI18n } from 'vue-i18n'

const { user, isBalancesVisible, toggleBalances } = useUser()
const isAddMoneyModalOpen = ref(false)
const { t } = useI18n()
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
        <div class="flex items-center gap-2">
          <Button variant="outline" @click="isAddMoneyModalOpen = true" class="rounded-full shadow-sm w-11 p-0 sm:w-auto sm:px-4">
            <Plus class="size-5 sm:mr-2 sm:size-4 shrink-0" />
            <span class="hidden sm:inline">{{ $t('home.addTransaction') }}</span>
          </Button>
          <Button variant="ghost" size="icon" @click="toggleBalances" class="text-muted-foreground hover:text-foreground">
            <Eye v-if="isBalancesVisible" class="size-5" />
            <EyeOff v-else class="size-5" />
          </Button>
        </div>
      </div>
      
      <AddMoneyModal v-model:open="isAddMoneyModalOpen" />

      <NetWorthCard />
      
      <div class="w-full">
        <SummaryCards />
      </div>

      <div class="w-full">
        <InvestmentsCard />
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
