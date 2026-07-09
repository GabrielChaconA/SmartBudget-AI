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

const computeNextDate = (dateStr: string, cycle: string) => {
  if (!dateStr) return new Date()
  
  // Parse 'YYYY-MM-DD' or full string correctly in local time to avoid timezone offset
  let date: Date;
  if (dateStr.includes('-') && dateStr.length === 10) {
    const [y, m, d] = dateStr.split('-')
    date = new Date(Number(y), Number(m) - 1, Number(d))
  } else {
    date = new Date(dateStr)
  }
  
  const now = new Date()
  now.setHours(0,0,0,0)
  
  while (date < now) {
    if (cycle === 'yearly') {
      date.setFullYear(date.getFullYear() + 1)
    } else {
      date.setMonth(date.getMonth() + 1)
    }
  }
  return date
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('es-MX', { month: 'short', day: 'numeric' })
}

const upcomingPayments = computed(() => {
  if (!user.value?.subscriptions) return []
  
  const active = user.value.subscriptions.filter((s: any) => s.status ? s.status === 'active' : true)
  
  const withRealDates = active.map((s: any) => {
    const nextDate = computeNextDate(s.next_billing_date, s.billing_cycle)
    return {
      id: s.id,
      name: s.name,
      when: formatDate(nextDate),
      timestamp: nextDate.getTime(),
      category: s.category || 'Suscripción',
      amount: parseFloat(s.amount)
    }
  })
  
  withRealDates.sort((a: any, b: any) => a.timestamp - b.timestamp)

  return withRealDates.slice(0, 4)
})
</script>

<template>
  <Card class="border-border">
    <CardHeader>
      <CardTitle>Próximos Pagos</CardTitle>
      <CardDescription>Suscripciones próximas a cobrar</CardDescription>
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
      <p v-if="upcomingPayments.length === 0" class="text-sm text-muted-foreground text-center py-4">No hay pagos programados.</p>
    </CardContent>
  </Card>
</template>
