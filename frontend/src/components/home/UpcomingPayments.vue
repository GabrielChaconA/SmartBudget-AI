<script setup lang="ts">
import { computed } from 'vue'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'

const { user } = useUser()

const upcomingPayments = computed(() => {
  if (!user.value?.subscriptions) return []
  
  // Filtrar activos y ordenar por fecha de cobro más próxima
  const active = user.value.subscriptions.filter((s: any) => s.status === 'active')
  
  active.sort((a: any, b: any) => {
    return new Date(a.next_billing_date).getTime() - new Date(b.next_billing_date).getTime()
  })

  // Tomar solo los primeros 4
  return active.slice(0, 4).map((s: any) => ({
    id: s.id,
    name: s.name,
    when: s.next_billing_date,
    category: s.category || 'Subscription',
    amount: parseFloat(s.amount)
  }))
})
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
            <span v-if="Number(i) < upcomingPayments.length - 1" class="my-1 w-px flex-1 bg-border" />
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
              {{ formatCurrency(payment.amount, user?.currency || 'MXN') }}
            </p>
          </div>
        </li>
      </ol>
      <p v-if="upcomingPayments.length === 0" class="text-sm text-muted-foreground text-center py-4">No upcoming payments scheduled.</p>
    </CardContent>
  </Card>
</template>
