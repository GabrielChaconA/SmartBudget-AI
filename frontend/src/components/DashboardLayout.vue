<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  LayoutDashboard,
  ChartColumnIncreasing,
  User,
  Bell,
  Settings,
  Search,
  Sparkles,
  CreditCard,
  TrendingUp,
  LogOut,
  Camera
} from '@lucide/vue'

import { cn } from "@/lib/utils"
import Logo from "@/components/Logo.vue"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useUser } from '@/composables/useUser'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { user } = useUser()
const { logout } = useAuth()

const navItems = [
  { href: "/", label: "Home", short: "Home", icon: LayoutDashboard },
  { href: "/analytics", label: "Analytics", short: "Stats", icon: ChartColumnIncreasing },
  { href: "/investments", label: "Investments", short: "Invest", icon: TrendingUp },
  { href: "/chat", label: "AI Chat", short: "Chat", icon: Sparkles },
  { href: "/memberships", label: "Memberships", short: "Subs", icon: CreditCard },
  { href: "/profile", label: "Profile", short: "Profile", icon: User },
]

const isActive = (href: string) => route.path === href
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Desktop sidebar -->
    <aside class="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-border bg-sidebar px-4 py-6 lg:flex">
      <div class="px-2">
        <Logo />
      </div>
      <nav class="mt-8 flex flex-col gap-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.href"
          :to="item.href"
          :class="cn(
            'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
            isActive(item.href)
              ? 'bg-sidebar-accent text-sidebar-accent-foreground'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          )"
        >
          <component :is="item.icon" class="size-5" aria-hidden="true" />
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>

    <div class="lg:pl-64">
      <!-- Header -->
      <header class="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-sm sm:px-6 lg:px-8">
        <div class="lg:hidden">
          <Logo :showWordmark="false" />
        </div>
        <div class="relative hidden flex-1 items-center md:flex">
          <Search class="pointer-events-none absolute left-3 size-4 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search transactions, accounts…"
            class="h-10 w-full max-w-sm rounded-xl border border-input bg-card pl-9 pr-3 text-sm text-foreground outline-none placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring/40"
          />
        </div>
        <div class="ml-auto flex items-center gap-1.5">
          <Button
            variant="ghost"
            size="icon"
            class="relative rounded-xl"
            aria-label="Notifications"
          >
            <Bell class="size-5" />
            <span class="absolute right-2 top-2 size-2 rounded-full bg-primary ring-2 ring-background" />
          </Button>

          <DropdownMenu v-if="user">
            <DropdownMenuTrigger as-child>
              <button class="ml-1 flex items-center gap-2 rounded-xl p-1 hover:bg-muted outline-none">
                <Avatar class="size-9">
                  <AvatarImage :src="user?.avatar || ''" :alt="user?.name || 'User'" />
                  <AvatarFallback>{{ user?.name ? user.name.substring(0, 2).toUpperCase() : 'ML' }}</AvatarFallback>
                </Avatar>
                <div class="hidden pr-2 text-left sm:block">
                  <p class="text-sm font-medium leading-none text-foreground">
                    {{ user.name || 'Anonymous' }}
                  </p>
                  <p class="mt-1 text-xs text-muted-foreground">Premium</p>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="router.push('/profile')" class="cursor-pointer">
                <User class="mr-2 size-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem class="cursor-pointer">
                <Settings class="mr-2 size-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="logout" class="cursor-pointer text-destructive focus:text-destructive">
                <LogOut class="mr-2 size-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <!-- Main content -->
      <main class="px-4 pb-24 pt-6 sm:px-6 lg:px-8 lg:pb-10">
        <slot />
      </main>
    </div>

    <!-- Mobile bottom navigation -->
    <nav class="fixed inset-x-0 bottom-0 z-30 flex border-t border-border bg-card lg:hidden">
      <RouterLink
        v-for="item in navItems"
        :key="item.href"
        :to="item.href"
        :class="cn(
          'flex flex-1 flex-col items-center gap-1 py-3 text-xs font-medium transition-colors',
          isActive(item.href) ? 'text-primary' : 'text-muted-foreground'
        )"
      >
        <component :is="item.icon" class="size-5" aria-hidden="true" />
        {{ item.short }}
      </RouterLink>
    </nav>
  </div>
</template>
