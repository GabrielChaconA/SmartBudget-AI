<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Logo from '@/components/Logo.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const GoogleIcon = {
  template: `
    <svg viewBox="0 0 24 24" class="size-4" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1Z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.65l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23Z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.11a6.6 6.6 0 0 1 0-4.22V7.05H2.18a11 11 0 0 0 0 9.9l3.66-2.84Z"
      />
      <path
        fill="#EA4335"
        d="M12 4.75c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 1.46 14.97.5 12 .5A11 11 0 0 0 2.18 7.05l3.66 2.84C6.71 6.68 9.14 4.75 12 4.75Z"
      />
    </svg>
  `
}
</script>

<template>
  <main class="flex min-h-screen flex-col lg:flex-row">
    <!-- Left: illustration panel (desktop) -->
    <section class="relative hidden w-1/2 flex-col justify-between border-r border-border bg-card p-12 lg:flex">
      <Logo />
      <div class="flex flex-1 items-center justify-center">
        <!-- Mock image for now since we don't have the original asset in public -->
        <div class="h-64 w-full max-w-md rounded-xl bg-gradient-to-tr from-primary/20 to-primary/5 flex items-center justify-center">
          <span class="text-primary/40 font-medium">Illustration</span>
        </div>
      </div>
      <div class="max-w-md">
        <h2 class="text-2xl font-semibold leading-snug tracking-tight text-foreground text-balance">
          Financial clarity, powered by intelligent insights.
        </h2>
        <p class="mt-3 text-sm leading-relaxed text-muted-foreground">
          Track every account, forecast your future, and let AI guide you
          toward your goals.
        </p>
      </div>
    </section>

    <!-- Right: login form -->
    <section class="flex flex-1 items-center justify-center px-6 py-12">
      <div class="w-full max-w-sm">
        <div class="mb-8 flex flex-col items-center gap-6 text-center lg:items-start lg:text-left">
          <div class="lg:hidden">
            <Logo />
          </div>
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-foreground">
              Welcome back
            </h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Sign in to your SmartBudget AI account.
            </p>
          </div>
        </div>

        <form class="flex flex-col gap-6" @submit.prevent="">
          <div class="space-y-4">
            <div class="space-y-2">
              <Label for="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                autocomplete="email"
                value="mariana.lopez@gmail.com"
              />
            </div>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <Label for="password">Password</Label>
                <RouterLink
                  to="#"
                  class="text-xs font-medium text-primary hover:underline"
                >
                  Forgot password?
                </RouterLink>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autocomplete="current-password"
                value="password"
              />
            </div>
          </div>

          <Button size="lg" class="w-full" as-child>
            <RouterLink to="/">
              Sign In
            </RouterLink>
          </Button>

          <div class="flex items-center gap-3">
            <span class="h-px flex-1 bg-border" />
            <span class="text-xs text-muted-foreground">or</span>
            <span class="h-px flex-1 bg-border" />
          </div>

          <Button variant="outline" size="lg" class="w-full">
            <GoogleIcon />
            Continue with Google
          </Button>
        </form>

        <p class="mt-8 text-center text-sm text-muted-foreground">
          Don't have an account?
          <RouterLink to="/" class="font-medium text-primary hover:underline">
            Sign up
          </RouterLink>
        </p>
      </div>
    </section>
  </main>
</template>
