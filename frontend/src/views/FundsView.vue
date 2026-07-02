<script setup lang="ts">
import { ref, computed } from 'vue'
import { Wallet, Plus, Search } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import CreateFundModal from '@/components/home/CreateFundModal.vue'
import FundDetailsModal from '@/components/home/FundDetailsModal.vue'

const { user } = useUser()
const searchQuery = ref('')
const isCreateModalOpen = ref(false)
const isDetailsModalOpen = ref(false)
const selectedFund = ref(null)

const openFundDetails = (fund: any) => {
  selectedFund.value = fund
  isDetailsModalOpen.value = true
}

const filteredFunds = computed(() => {
  if (!user.value?.funds) return []
  if (!searchQuery.value) return user.value.funds
  const lower = searchQuery.value.toLowerCase()
  return user.value.funds.filter((f: any) => f.name.toLowerCase().includes(lower))
})
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-foreground">
            Funds
          </h1>
          <p class="mt-1 text-sm text-muted-foreground">
            Manage your money pockets and allocations.
          </p>
        </div>
        <div class="relative w-full sm:w-64">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input v-model="searchQuery" placeholder="Search by name..." class="pl-9" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <!-- New Fund Card inside the grid -->
        <Card class="border-border border-dashed cursor-pointer hover:border-primary/50 transition-colors flex items-center justify-center bg-muted/10 min-h-[140px]" @click="isCreateModalOpen = true">
          <CardContent class="flex flex-col items-center justify-center p-5 text-center h-full w-full opacity-60 hover:opacity-100 transition-opacity">
            <div class="flex size-10 items-center justify-center rounded-xl bg-accent mb-3 text-muted-foreground">
              <Plus class="size-5" />
            </div>
            <p class="text-sm font-medium text-muted-foreground">New Fund</p>
          </CardContent>
        </Card>

        <Card
          v-for="fund in filteredFunds"
          :key="fund.id"
          class="border-border cursor-pointer hover:border-primary/50 transition-colors"
          @click="openFundDetails(fund)"
        >
          <CardContent class="flex flex-col gap-4 p-5">
            <div class="flex items-center justify-between">
              <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground" :style="fund.color ? { color: fund.color } : {}">
                <Wallet class="size-5" />
              </div>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">{{ fund.name }}</p>
              <p class="mt-1 text-2xl font-semibold tracking-tight text-foreground">
                {{ formatCurrency(fund.balance, user?.currency || 'MXN') }}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div v-if="filteredFunds.length === 0 && searchQuery" class="text-center py-10 text-muted-foreground">
        No funds found matching "{{ searchQuery }}"
      </div>
    </div>
    
    <CreateFundModal v-model:open="isCreateModalOpen" />
    <FundDetailsModal v-model:open="isDetailsModalOpen" :fund="selectedFund" />
  </DashboardLayout>
</template>
