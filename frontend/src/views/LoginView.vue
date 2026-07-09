<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import Logo from '@/components/Logo.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAuth } from '@/composables/useAuth'
import { Loader2 } from '@lucide/vue'

const activeTab = ref('login')

// Login refs
const email = ref('')
const password = ref('')

// Register refs
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regPasswordConfirm = ref('')

const { login, register, isLoading, error } = useAuth()
const router = useRouter()
const route = useRoute()

onMounted(() => {
  // Ensure dark mode is applied if they want it black
  document.documentElement.classList.add('dark')

  if (route.query.token) {
    const token = route.query.token as string;
    localStorage.setItem('auth_token', token);
    import('axios').then(({ default: axios }) => {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      router.push('/');
    });
  } else if (route.query.error) {
    error.value = 'Google Login failed. Please try again.';
  }
})

const handleLogin = async () => {
  const success = await login(email.value, password.value)
  if (success) {
    router.push('/')
  }
}

const handleRegister = async () => {
  if (regPassword.value !== regPasswordConfirm.value) {
    error.value = "Passwords don't match";
    return
  }
  if (register) {
    const success = await register(regName.value, regEmail.value, regPassword.value)
    if (success) router.push('/')
  }
}

const handleGoogleLogin = () => {
  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  window.location.href = `${apiBase}/api/auth/google/redirect`
}

const GoogleIcon = {
  template: `
    <svg viewBox="0 0 24 24" class="size-4" aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1Z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.65l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23Z" />
      <path fill="#FBBC05" d="M5.84 14.11a6.6 6.6 0 0 1 0-4.22V7.05H2.18a11 11 0 0 0 0 9.9l3.66-2.84Z" />
      <path fill="#EA4335" d="M12 4.75c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 1.46 14.97.5 12 .5A11 11 0 0 0 2.18 7.05l3.66 2.84C6.71 6.68 9.14 4.75 12 4.75Z" />
    </svg>
  `
}
</script>

<template>
  <main class="flex min-h-screen flex-col lg:flex-row dark bg-background text-foreground">
    <!-- Left: illustration panel (desktop only) -->
    <section class="relative hidden w-1/2 lg:flex overflow-hidden bg-cover bg-center" style="background-image: url('/login.jpeg');">
      <div class="absolute inset-0 bg-black/60"></div>
      
      <div class="relative z-10 w-full h-full hidden lg:flex flex-col items-center justify-center p-6 lg:p-12 text-white gap-4 lg:gap-8">
        <h1 class="text-5xl lg:text-7xl font-extrabold tracking-tighter text-balance text-center drop-shadow-2xl">
          SmartBudget <span class="text-primary">AI</span>
        </h1>
        
        <div class="text-center w-full">
          <h2 class="text-2xl lg:text-3xl font-semibold leading-snug tracking-tight text-balance">
            Financial clarity, powered by intelligent insights.
          </h2>
          <p class="mt-3 text-lg leading-relaxed text-gray-200">
            Track every account, forecast your future, and let AI guide you
            toward your goals.
          </p>
        </div>
      </div>
    </section>

    <!-- Right: login form -->
    <section class="flex flex-1 flex-col items-center justify-start lg:justify-center lg:px-6 py-0 lg:py-12 relative overflow-y-auto w-full">
      <div class="w-full lg:max-w-sm">
        
        <!-- Mobile Header with background / Desktop Header normal -->
        <div class="mb-6 lg:mb-8 flex flex-col items-center justify-center gap-4 lg:gap-6 text-center 
                    bg-[url('/login.jpeg')] bg-cover bg-center lg:bg-none 
                    px-6 py-16 lg:px-0 lg:py-0 relative">
          
          <div class="absolute inset-0 bg-black/60 lg:hidden"></div>
          
          <div class="relative z-10 flex flex-col items-center">
            <Logo class="h-10 w-auto lg:hidden mb-2" />
            <h1 class="text-4xl font-bold tracking-tight text-white lg:text-foreground">
              Welcome
            </h1>
            <p class="mt-2 text-sm text-gray-200 lg:text-muted-foreground">
              Sign in or create an account to continue.
            </p>
          </div>
        </div>

        <div class="px-6 lg:px-0">
          <Tabs v-model="activeTab" class="w-full flex-col">
          <TabsList class="grid w-full grid-cols-2 mb-6 h-12 bg-zinc-900/50">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <form class="flex flex-col gap-6" @submit.prevent="handleLogin">
              <div v-if="error && activeTab === 'login'" class="p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
                {{ error }}
              </div>
              <div class="space-y-4">
                <div class="space-y-2 text-left">
                  <Label for="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    v-model="email"
                    placeholder="you@example.com"
                    autocomplete="email"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
                <div class="space-y-2 text-left">
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
                    v-model="password"
                    placeholder="••••••••"
                    autocomplete="current-password"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
              </div>

              <Button type="submit" class="w-full h-12 text-base font-semibold" :disabled="isLoading">
                <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                Sign In
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="register">
            <form class="flex flex-col gap-6" @submit.prevent="handleRegister">
              <div v-if="error && activeTab === 'register'" class="p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
                {{ error }}
              </div>
              <div class="space-y-4">
                <div class="space-y-2 text-left">
                  <Label for="regName">Name</Label>
                  <Input
                    id="regName"
                    type="text"
                    v-model="regName"
                    placeholder="John Doe"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
                <div class="space-y-2 text-left">
                  <Label for="regEmail">Email</Label>
                  <Input
                    id="regEmail"
                    type="email"
                    v-model="regEmail"
                    placeholder="you@example.com"
                    autocomplete="email"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
                <div class="space-y-2 text-left">
                  <Label for="regPassword">Password</Label>
                  <Input
                    id="regPassword"
                    type="password"
                    v-model="regPassword"
                    placeholder="••••••••"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
                <div class="space-y-2 text-left">
                  <Label for="regPasswordConfirm">Confirm Password</Label>
                  <Input
                    id="regPasswordConfirm"
                    type="password"
                    v-model="regPasswordConfirm"
                    placeholder="••••••••"
                    class="h-12 px-4 text-base bg-zinc-900/50 border-zinc-800 focus-visible:ring-primary"
                    required
                  />
                </div>
              </div>

              <Button type="submit" class="w-full h-12 text-base font-semibold" :disabled="isLoading">
                <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
                Sign Up
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        <div class="mt-6 flex flex-col gap-6 w-full">
          <div class="flex items-center gap-3">
            <span class="h-px flex-1 bg-border" />
            <span class="text-xs text-muted-foreground">or</span>
            <span class="h-px flex-1 bg-border" />
          </div>

          <Button variant="outline" class="w-full h-12 text-base font-medium bg-zinc-900/30 border-zinc-800 hover:bg-zinc-800" @click="handleGoogleLogin">
            <GoogleIcon />
            Continue with Google
          </Button>
        </div>
        </div>

      </div>
    </section>
  </main>
</template>
