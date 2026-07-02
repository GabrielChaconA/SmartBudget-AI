<script setup lang="ts">
import { TrendingUp } from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useUser } from '@/composables/useUser'
import { computed } from 'vue'
import { netWorth, formatCurrency } from '@/lib/data'

const { user } = useUser()

const totalBalance = computed(() => {
  let sum = 0
  if (user.value?.accounts) {
    sum += user.value.accounts.reduce((acc: number, a: any) => acc + parseFloat(a.balance), 0)
  }
  if (user.value?.funds) {
    sum += user.value.funds.reduce((acc: number, f: any) => acc + parseFloat(f.balance), 0)
  }
  return sum
})
</script>

<template>
  <Card class="overflow-hidden border-border bg-primary text-primary-foreground">
    <CardContent class="flex flex-col gap-6 p-6 sm:p-8 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-medium text-primary-foreground/80">
          Total Net Worth
        </p>
        <p class="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
          {{ formatCurrency(totalBalance, user?.currency || 'MXN') }}
        </p>
        <div class="mt-4 flex flex-wrap items-center gap-2">
          <Badge class="border-0 bg-primary-foreground/15 text-primary-foreground">
            <TrendingUp class="size-3.5 mr-1" />+{{ netWorth.changePercent }}%
          </Badge>
          <span class="text-sm text-primary-foreground/80">
            +{{ formatCurrency(netWorth.changeAmount, user?.currency || 'MXN') }} today
          </span>
        </div>
      </div>
      <div class="flex items-end gap-1.5" aria-hidden="true">
        <span
          v-for="(h, i) in [40, 55, 48, 64, 58, 72, 68, 82, 90]"
          :key="i"
          class="w-3 rounded-full bg-primary-foreground/30 sm:w-4"
          :style="{ height: `${h}px` }"
        />
      </div>
    </CardContent>
  </Card>
</template>
