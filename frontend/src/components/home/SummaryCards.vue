<script setup lang="ts">
import { ref } from 'vue'
import {
  Wallet,
  Plus,
  Eye,
  EyeOff
} from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import CreateFundModal from './CreateFundModal.vue'
import FundDetailsModal from './FundDetailsModal.vue'

const { user, isBalancesVisible, isItemVisible, toggleItemVisibility } = useUser()

const isCreateModalOpen = ref(false)
const isDetailsModalOpen = ref(false)
const selectedFund = ref(null)

import { RouterLink } from 'vue-router'

const openFundDetails = (fund: any) => {
  selectedFund.value = fund
  isDetailsModalOpen.value = true
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold tracking-tight text-foreground">Your Funds</h2>
      <RouterLink to="/funds" class="text-sm font-medium text-primary hover:underline">
        See all
      </RouterLink>
    </div>
    
    <div v-if="user?.funds?.length > 0" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <!-- New Fund Card inside the grid -->
      <Card 
        class="flex border-border border-dashed cursor-pointer hover:border-primary/50 transition-colors items-center justify-center bg-muted/10 min-h-[140px]" 
        @click="isCreateModalOpen = true"
      >
        <CardContent class="flex flex-col items-center justify-center p-5 text-center h-full w-full opacity-60 hover:opacity-100 transition-opacity">
          <div class="flex size-10 items-center justify-center rounded-xl bg-accent mb-3 text-muted-foreground">
            <Plus class="size-5" />
          </div>
          <p class="text-sm font-medium text-muted-foreground">New Fund</p>
        </CardContent>
      </Card>

      <Card
        v-for="fund in user?.funds?.slice(0, 3)"
        :key="fund.id"
        class="border-border cursor-pointer hover:border-primary/50 transition-colors"
        @click="openFundDetails(fund)"
      >
        <CardContent class="flex flex-col gap-4 p-5">
          <div class="flex items-center justify-between">
            <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground" :style="fund.color ? { color: fund.color } : {}">
              <Wallet class="size-5" />
            </div>
            <Button variant="ghost" size="icon" @click.stop="toggleItemVisibility(`fund_${fund.id}`)" class="h-8 w-8 text-muted-foreground hover:text-foreground">
              <Eye v-if="isItemVisible(`fund_${fund.id}`)" class="size-4" />
              <EyeOff v-else class="size-4" />
            </Button>
          </div>
          <div>
            <p class="text-sm text-muted-foreground">{{ fund.name }}</p>
            <p class="mt-1 text-2xl font-semibold tracking-tight text-foreground">
              <span v-if="isItemVisible(`fund_${fund.id}`)">{{ formatCurrency(fund.balance, user?.currency || 'MXN') }}</span>
              <span v-else>••••••</span>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
    
    <Card v-else class="border-border border-dashed">
      <CardContent class="flex flex-col items-center justify-center p-8 text-center">
        <div class="flex size-12 items-center justify-center rounded-full bg-accent mb-4">
          <Wallet class="size-6 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-medium text-foreground">No funds created yet</h3>
        <p class="mt-2 text-sm text-muted-foreground max-w-sm mb-4">
          Create pockets of money to organize your finances.
        </p>
        <Button variant="outline" @click="isCreateModalOpen = true">
          <Plus class="size-4 mr-2" />
          Create Fund
        </Button>
      </CardContent>
    </Card>

    <CreateFundModal v-model:open="isCreateModalOpen" />
    <FundDetailsModal v-model:open="isDetailsModalOpen" :fund="selectedFund" />
  </div>
</template>
