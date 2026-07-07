<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent } from '@/components/ui/card'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import { TrendingUp, Layers } from '@lucide/vue'
import { RouterLink, useRouter } from 'vue-router'

const { user, totalInvestmentsAmount } = useUser()
const router = useRouter()

const totalInvestments = computed(() => totalInvestmentsAmount.value)

const numInvestments = computed(() => user.value?.investments?.length || 0)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold tracking-tight text-foreground">Investments</h2>
      <RouterLink to="/investments" class="text-sm font-medium text-primary hover:underline">
        Manage
      </RouterLink>
    </div>
    
    <Card @click="router.push('/investments')" class="border-border cursor-pointer hover:border-primary/50 transition-colors bg-gradient-to-br from-card to-card/50">
      <CardContent class="flex flex-col gap-4 p-5">
        <div class="flex items-center justify-between">
          <div class="flex size-10 items-center justify-center rounded-xl bg-blue-500/15 text-blue-500">
            <TrendingUp class="size-5" />
          </div>
          <span class="text-xs font-medium bg-blue-500/10 text-blue-500 px-2 py-1 rounded-full flex items-center gap-1">
            <Layers class="size-3" /> {{ numInvestments }} Active
          </span>
        </div>
        <div>
          <p class="text-sm text-muted-foreground">Current Value</p>
          <p class="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {{ formatCurrency(totalInvestments, user?.currency || 'MXN') }}
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
