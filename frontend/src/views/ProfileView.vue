<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Pencil, Shield, LogOut, Target, Crown, Landmark, LineChart } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { user, linkedAccounts, investmentAccounts, formatCurrency } from '@/lib/data'

const goals = [
  { label: 'Emergency fund', current: 68 },
  { label: 'Vacation 2026', current: 42 },
  { label: 'New apartment', current: 25 },
]
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-foreground">
          Profile
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          Manage your account, goals and preferences.
        </p>
      </div>

      <!-- Identity header -->
      <Card class="border-border">
        <CardContent class="flex flex-col gap-6 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
            <div class="flex size-20 items-center justify-center overflow-hidden rounded-full bg-muted">
              <img v-if="user.avatar" :src="user.avatar" :alt="user.name" class="h-full w-full object-cover" />
              <span v-else class="text-xl font-medium text-muted-foreground">ML</span>
            </div>
            <div>
              <div class="flex items-center justify-center gap-2 sm:justify-start">
                <h2 class="text-xl font-semibold text-foreground">
                  {{ user.name }}
                </h2>
                <Badge>
                  <Crown class="size-3 mr-1" />
                  Premium
                </Badge>
              </div>
              <p class="mt-1 text-sm text-muted-foreground">
                {{ user.email }}
              </p>
              <p class="mt-1 text-sm text-muted-foreground">
                Monthly income {{ formatCurrency(user.monthlyIncome, user.currency) }}
              </p>
            </div>
          </div>
          <div class="flex flex-wrap justify-center gap-3">
            <Button>
              <Pencil class="mr-2 h-4 w-4" />
              Edit Profile
            </Button>
            <Button variant="outline">
              <Shield class="mr-2 h-4 w-4" />
              Privacy Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Left column -->
        <div class="flex flex-col gap-6 lg:col-span-2">
          
          <!-- Linked Accounts -->
          <Card class="border-border">
            <CardHeader class="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Linked Accounts</CardTitle>
                <CardDescription>Bank and card connections</CardDescription>
              </div>
              <Button variant="outline" size="sm">Manage Accounts</Button>
            </CardHeader>
            <CardContent class="flex flex-col gap-3">
              <div v-for="a in linkedAccounts" :key="a.id" class="flex items-center justify-between gap-4 rounded-xl border border-border p-4">
                <div class="flex items-center gap-3">
                  <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
                    <Landmark class="size-5" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-foreground">{{ a.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ a.type }} · {{ a.number }}</p>
                  </div>
                </div>
                <p :class="[
                  'text-sm font-semibold tabular-nums',
                  a.balance < 0 ? 'text-destructive' : 'text-foreground'
                ]">
                  {{ formatCurrency(a.balance, user.currency) }}
                </p>
              </div>
            </CardContent>
          </Card>

          <!-- Investment Accounts -->
          <Card class="border-border">
            <CardHeader>
              <CardTitle>Investment Accounts</CardTitle>
              <CardDescription>Brokerage and crypto holdings</CardDescription>
            </CardHeader>
            <CardContent class="flex flex-col gap-3">
              <div v-for="a in investmentAccounts" :key="a.id" class="flex items-center justify-between gap-4 rounded-xl border border-border p-4">
                <div class="flex items-center gap-3">
                  <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
                    <LineChart class="size-5" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-foreground">{{ a.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ a.type }} · {{ a.number }}</p>
                  </div>
                </div>
                <p :class="[
                  'text-sm font-semibold tabular-nums',
                  a.balance < 0 ? 'text-destructive' : 'text-foreground'
                ]">
                  {{ formatCurrency(a.balance, user.currency) }}
                </p>
              </div>
            </CardContent>
          </Card>

        </div>

        <!-- Right column -->
        <div class="flex flex-col gap-6">
          <Card class="border-border">
            <CardHeader>
              <CardTitle>Financial Goals</CardTitle>
              <CardDescription>Progress toward your targets</CardDescription>
            </CardHeader>
            <CardContent class="flex flex-col gap-5">
              <div v-for="goal in goals" :key="goal.label" class="flex flex-col gap-2">
                <div class="flex items-center justify-between text-sm">
                  <span class="flex items-center gap-2 font-medium text-foreground">
                    <Target class="size-4 text-primary" />
                    {{ goal.label }}
                  </span>
                  <span class="text-muted-foreground">
                    {{ goal.current }}%
                  </span>
                </div>
                <div class="h-2.5 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    class="h-full rounded-full bg-primary"
                    :style="{ width: `${goal.current}%` }"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="border-border bg-accent">
            <CardHeader>
              <CardTitle class="text-accent-foreground">
                Subscription
              </CardTitle>
              <CardDescription>SmartBudget AI Premium</CardDescription>
            </CardHeader>
            <CardContent class="flex flex-col gap-4">
              <div class="flex items-baseline gap-1">
                <span class="text-2xl font-semibold text-foreground">
                  $149
                </span>
                <span class="text-sm text-muted-foreground">/ month</span>
              </div>
              <p class="text-sm leading-relaxed text-muted-foreground">
                Renews on October 24, 2025. Includes unlimited AI insights and
                advanced forecasting.
              </p>
              <Button variant="outline" class="w-full">
                Manage Subscription
              </Button>
            </CardContent>
          </Card>

          <Button variant="outline" class="w-full" as-child>
            <RouterLink to="/login">
              <LogOut class="mr-2 h-4 w-4" />
              Logout
            </RouterLink>
          </Button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>
