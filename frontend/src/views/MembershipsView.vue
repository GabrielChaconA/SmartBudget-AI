<script setup lang="ts">
import { ref, computed } from 'vue'
import { Bell, BellOff, CreditCard, CalendarClock } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { memberships as initialMemberships, formatCurrency } from '@/lib/data'

const memberships = ref(initialMemberships)

function toggleNotify(id: string) {
  const m = memberships.value.find(x => x.id === id)
  if (m) m.notify = !m.notify
}

const active = computed(() => memberships.value.filter(m => m.active))
const inactive = computed(() => memberships.value.filter(m => !m.active))

const monthlyTotal = computed(() => 
  active.value.reduce((sum, m) => sum + (m.cycle === 'Yearly' ? m.amount / 12 : m.amount), 0)
)
const notifyCount = computed(() => active.value.filter(m => m.notify).length)
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-5xl">
      <header class="pb-6">
        <h1 class="text-2xl font-semibold tracking-tight text-foreground">
          Active Memberships
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          Manage your subscriptions and choose which ones send you payment reminders.
        </p>
      </header>

      <!-- Summary -->
      <div class="grid gap-4 sm:grid-cols-3">
        <Card class="border-border">
          <CardHeader class="flex-row items-center gap-3 space-y-0">
            <span class="flex size-10 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <CreditCard class="size-5" />
            </span>
            <div>
              <CardDescription>Active subscriptions</CardDescription>
              <CardTitle class="text-xl">{{ active.length }}</CardTitle>
            </div>
          </CardHeader>
        </Card>
        <Card class="border-border">
          <CardHeader class="flex-row items-center gap-3 space-y-0">
            <span class="flex size-10 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <CalendarClock class="size-5" />
            </span>
            <div>
              <CardDescription>Est. monthly cost</CardDescription>
              <CardTitle class="text-xl">{{ formatCurrency(monthlyTotal) }}</CardTitle>
            </div>
          </CardHeader>
        </Card>
        <Card class="border-border">
          <CardHeader class="flex-row items-center gap-3 space-y-0">
            <span class="flex size-10 items-center justify-center rounded-xl bg-primary/15 text-primary">
              <Bell class="size-5" />
            </span>
            <div>
              <CardDescription>Notifications on</CardDescription>
              <CardTitle class="text-xl">{{ notifyCount }} of {{ active.length }}</CardTitle>
            </div>
          </CardHeader>
        </Card>
      </div>

      <!-- Active list -->
      <section class="mt-8">
        <div class="mb-3 flex items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Active
          </h2>
          <Badge variant="secondary">{{ active.length }}</Badge>
        </div>
        <Card class="border-border">
          <CardContent class="divide-y divide-border p-0">
            <div
              v-for="m in active"
              :key="m.id"
              class="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:px-6"
            >
              <div class="flex flex-1 items-center gap-4">
                <span class="flex size-10 items-center justify-center rounded-xl bg-secondary text-foreground">
                  <CreditCard class="size-5" />
                </span>
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <p class="truncate font-medium text-foreground">{{ m.name }}</p>
                    <Badge variant="secondary" class="hidden sm:inline-flex">
                      {{ m.category }}
                    </Badge>
                  </div>
                  <p class="text-sm text-muted-foreground">
                    {{ m.plan }} · Renews {{ m.nextCharge }}
                  </p>
                </div>
              </div>

              <div class="flex items-center justify-between gap-4 sm:justify-end">
                <div class="text-right">
                  <p class="font-semibold text-foreground">{{ formatCurrency(m.amount) }}</p>
                  <p class="text-xs text-muted-foreground">{{ m.cycle }}</p>
                </div>

                <Separator orientation="vertical" class="hidden h-10 sm:block" />

                <div class="flex items-center gap-2">
                  <Label
                    :for="`notify-${m.id}`"
                    :class="[
                      'flex items-center gap-1.5 text-sm',
                      m.notify ? 'text-foreground' : 'text-muted-foreground'
                    ]"
                  >
                    <Bell v-if="m.notify" class="size-4 text-primary" />
                    <BellOff v-else class="size-4" />
                    <span class="hidden sm:inline">Notify</span>
                  </Label>
                  <Switch
                    :id="`notify-${m.id}`"
                    :checked="m.notify"
                    @update:checked="toggleNotify(m.id)"
                    :aria-label="`Toggle notifications for ${m.name}`"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      <!-- Inactive list -->
      <section v-if="inactive.length > 0" class="mt-8">
        <div class="mb-3 flex items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Inactive
          </h2>
          <Badge variant="outline">{{ inactive.length }}</Badge>
        </div>
        <Card class="border-border">
          <CardContent class="divide-y divide-border p-0">
            <div
              v-for="m in inactive"
              :key="m.id"
              class="flex items-center gap-4 px-4 py-4 opacity-60 sm:px-6"
            >
              <span class="flex size-10 items-center justify-center rounded-xl bg-muted text-muted-foreground">
                <CreditCard class="size-5" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-foreground">{{ m.name }}</p>
                <p class="text-sm text-muted-foreground">{{ m.nextCharge }}</p>
              </div>
              <span class="text-sm font-medium text-muted-foreground">
                {{ formatCurrency(m.amount) }}
              </span>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  </DashboardLayout>
</template>
