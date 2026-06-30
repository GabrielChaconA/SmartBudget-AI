<script setup lang="ts">
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card'
import { upcomingPayments, formatCurrency, user } from '@/lib/data'
</script>

<template>
  <Card class="border-border">
    <CardHeader>
      <CardTitle>Upcoming Payments</CardTitle>
      <CardDescription>Scheduled over the next two weeks</CardDescription>
    </CardHeader>
    <CardContent>
      <ol class="relative flex flex-col">
        <li v-for="(payment, i) in upcomingPayments" :key="payment.id" class="flex gap-4">
          <div class="flex flex-col items-center">
            <span class="mt-1.5 size-2.5 shrink-0 rounded-full bg-primary" />
            <span v-if="i < upcomingPayments.length - 1" class="my-1 w-px flex-1 bg-border" />
          </div>
          <div class="flex flex-1 items-start justify-between pb-6">
            <div>
              <p class="text-sm font-medium text-foreground">
                {{ payment.name }}
              </p>
              <p class="mt-0.5 text-xs text-muted-foreground">
                {{ payment.when }} &middot; {{ payment.category }}
              </p>
            </div>
            <p class="text-sm font-semibold text-foreground">
              {{ formatCurrency(payment.amount, user.currency) }}
            </p>
          </div>
        </li>
      </ol>
    </CardContent>
  </Card>
</template>
