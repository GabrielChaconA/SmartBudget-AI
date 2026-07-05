<script setup lang="ts">

import { Pencil, Shield, LogOut, Target, Crown, Landmark, LineChart, Loader2 } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import { useAuth } from '@/composables/useAuth'
import EditProfileModal from '@/components/EditProfileModal.vue'
import AvatarCropModal from '@/components/AvatarCropModal.vue'
import { ref, computed } from 'vue'

const { user, isLoading: isUserLoading, error: userError, uploadAvatar } = useUser()
const { logout } = useAuth()
const isEditModalOpen = ref(false)
const isCropModalOpen = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
    isCropModalOpen.value = true;
    target.value = ''; // reset
  }
}

const handleCrop = async (blob: Blob) => {
  isCropModalOpen.value = false;
  // Convert blob to File so uploadAvatar accepts it
  const croppedFile = new File([blob], 'avatar-cropped.jpg', { type: blob.type || 'image/jpeg' });
  await uploadAvatar(croppedFile);
}

const goals = computed(() => {
  if (!user.value?.goals) return []
  return user.value.goals.map((g: any) => {
    let current = 0;
    if (g.target_amount > 0) {
      current = Math.min(100, Math.round((g.current_amount / g.target_amount) * 100));
    }
    return { label: g.name, current }
  })
})

const linkedAccounts = computed(() => {
  if (!user.value?.accounts) return []
  return user.value.accounts.filter((a: any) => a.type !== 'investment')
})

const investmentAccounts = computed(() => {
  if (!user.value?.accounts) return []
  return user.value.accounts.filter((a: any) => a.type === 'investment')
})

function getInitials(name: string) {
  if (!name) return '?'
  const parts = name.split(' ').filter(Boolean)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return '?'
}
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

      <input type="file" accept="image/*" class="hidden" ref="fileInput" @change="handleFileChange" />

      <!-- Identity header -->
      <Card class="border-border min-h-[160px] flex flex-col justify-center">
        <CardContent v-if="isUserLoading" class="flex flex-col items-center justify-center py-6 text-muted-foreground">
          <Loader2 class="size-6 animate-spin mb-2" />
          <p>Loading profile...</p>
        </CardContent>
        <CardContent v-else-if="userError" class="flex flex-col items-center justify-center py-6 text-destructive">
          <p>{{ userError }}</p>
        </CardContent>
        <CardContent v-else-if="user" class="flex flex-col gap-6 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
            <div 
              class="flex size-20 items-center justify-center overflow-hidden rounded-full bg-muted cursor-pointer hover:opacity-80 transition-opacity" 
              @click="fileInput?.click()"
              title="Change profile picture"
            >
              <img v-if="user.avatar" :src="user.avatar" :alt="user.name || 'User'" class="h-full w-full object-cover" />
              <span v-else class="text-xl font-medium text-muted-foreground">{{ getInitials(user.name || '') }}</span>
            </div>
            <div>
              <div class="flex items-center justify-center gap-2 sm:justify-start">
                <h2 class="text-xl font-semibold text-foreground">
                  {{ user.name || 'Anonymous' }}
                </h2>
              </div>
              <p class="mt-1 text-sm text-muted-foreground">
                {{ user.email || 'No email provided' }}
              </p>
              <p v-if="user.monthlyIncome !== undefined" class="mt-1 text-sm text-muted-foreground">
                Monthly income {{ formatCurrency(user.monthlyIncome, user.currency || 'USD') }}
              </p>
            </div>
          </div>
          <div class="flex flex-wrap justify-center gap-3">
            <Button class="bg-green-600 hover:bg-green-700 text-white" @click="isEditModalOpen = true">
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
                    <p class="text-xs text-muted-foreground capitalize">{{ a.type }}</p>
                  </div>
                </div>
                <p :class="[
                  'text-sm font-semibold tabular-nums',
                  a.balance < 0 ? 'text-destructive' : 'text-foreground'
                ]">
                  {{ formatCurrency(a.balance, user?.currency || 'USD') }}
                </p>
              </div>
              <p v-if="linkedAccounts.length === 0" class="text-sm text-muted-foreground py-4 text-center">No accounts linked yet.</p>
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
                    <p class="text-xs text-muted-foreground capitalize">{{ a.type }}</p>
                  </div>
                </div>
                <p :class="[
                  'text-sm font-semibold tabular-nums',
                  a.balance < 0 ? 'text-destructive' : 'text-foreground'
                ]">
                  {{ formatCurrency(a.balance, user?.currency || 'USD') }}
                </p>
              </div>
              <p v-if="investmentAccounts.length === 0" class="text-sm text-muted-foreground py-4 text-center">No investment accounts linked.</p>
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
              <p v-if="goals.length === 0" class="text-sm text-muted-foreground py-2 text-center">No goals set up yet.</p>
            </CardContent>
          </Card>


          <Button variant="outline" class="w-full" @click="logout">
            <LogOut class="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>
    </div>
    <EditProfileModal v-model:open="isEditModalOpen" />
    <AvatarCropModal 
      v-model:open="isCropModalOpen" 
      :file="selectedFile" 
      @crop="handleCrop" 
    />
  </DashboardLayout>
</template>
