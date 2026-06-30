<script setup lang="ts">
import {
  Wallet,
  CreditCard,
  PiggyBank,
  CalendarClock,
  ArrowUpRight,
  ArrowDownRight,
} from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { summaryCards, formatCurrency, user } from '@/lib/data'

const icons = {
  cash: Wallet,
  expenses: CreditCard,
  savings: PiggyBank,
  upcoming: CalendarClock,
} as const
</script>

<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <Card
      v-for="card in summaryCards"
      :key="card.id"
      class="border-border"
    >
      <CardContent class="flex flex-col gap-4 p-5">
        <div class="flex items-center justify-between">
          <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
            <component :is="icons[card.id as keyof typeof icons]" class="size-5" />
          </div>
          <span
            v-if="card.change !== 0"
            :class="cn(
              'flex items-center gap-0.5 text-xs font-medium',
              card.change > 0 ? 'text-success' : 'text-destructive'
            )"
          >
            <ArrowUpRight v-if="card.change > 0" class="size-3.5" />
            <ArrowDownRight v-else class="size-3.5" />
            {{ Math.abs(card.change) }}%
          </span>
        </div>
        <div>
          <p class="text-sm text-muted-foreground">{{ card.title }}</p>
          <p class="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {{ formatCurrency(card.value, user.currency) }}
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
