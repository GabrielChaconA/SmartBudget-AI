<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import { useInvestments } from '@/composables/useInvestments'
import { Layers, Building2, Bitcoin, Dices, Eye, EyeOff } from '@lucide/vue'
import { RouterLink } from 'vue-router'

const { user, isItemVisible, toggleItemVisibility } = useUser()
const { activeCategories, totalPortfolioValue, exchangeRate } = useInvestments()

const displayCurrency = computed(() => user.value?.currency || 'MXN')

const getDisplayValue = (val: number) => {
  if (!val) return 0
  const userCurrency = user.value?.currency || 'MXN'
  if (userCurrency === 'MXN' && displayCurrency.value === 'USD') return val / exchangeRate.value
  if (userCurrency === 'USD' && displayCurrency.value === 'MXN') return val * exchangeRate.value
  return val
}

const categoryIcons: Record<string, any> = {
  etfs: Layers,
  stocks: Building2,
  crypto: Bitcoin,
  bets: Dices
}

// Same filter as the Summary card in InvestmentsView when activeCat === 'all'
const visibleCategories = computed(() =>
  activeCategories.value.filter(c => c.id !== 'all' && c.value > 0)
)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold tracking-tight text-foreground">Investments</h2>
      <RouterLink to="/investments" class="text-sm font-medium text-primary hover:underline">
        Manage
      </RouterLink>
    </div>

    <Card class="border-border transition-colors">
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle class="text-base flex items-center gap-2">
            Summary
            <Button variant="ghost" size="icon" @click.stop="toggleItemVisibility('invest_summary')" class="h-6 w-6 text-muted-foreground hover:text-foreground">
              <Eye v-if="isItemVisible('invest_summary')" class="size-3" />
              <EyeOff v-else class="size-3" />
            </Button>
          </CardTitle>
        </div>
        <CardDescription>Portfolio breakdown.</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-3">
        <template v-if="visibleCategories.length > 0">
          <div v-for="cat in visibleCategories" :key="cat.id" class="flex items-center justify-between">
            <span class="text-sm text-muted-foreground flex items-center gap-2">
              <component :is="categoryIcons[cat.id]" class="size-4" />
              {{ cat.label }}
            </span>
            <span class="font-semibold tabular-nums text-foreground">
              <span v-if="isItemVisible('invest_summary')">{{ formatCurrency(getDisplayValue(cat.value), displayCurrency) }}</span>
              <span v-else>••••••</span>
            </span>
          </div>
        </template>

        <div v-else class="text-sm text-muted-foreground text-center py-2">
          No active investments
        </div>

        <div class="h-px w-full bg-border my-1"></div>

        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-foreground">Total</span>
          <span class="font-bold tabular-nums text-primary">
            <span v-if="isItemVisible('invest_summary')">
              {{ formatCurrency(getDisplayValue(totalPortfolioValue), displayCurrency) }}
            </span>
            <span v-else>••••••</span>
          </span>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
