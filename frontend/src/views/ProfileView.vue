<script setup lang="ts">

import { Pencil, Shield, LogOut, ChevronRight, Moon, Sun, HelpCircle, ShieldCheck, Palette } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatCurrency } from '@/lib/data'
import { useUser } from '@/composables/useUser'
import { useAuth } from '@/composables/useAuth'
import { useDark, useToggle } from '@vueuse/core'
import EditProfileModal from '@/components/EditProfileModal.vue'
import AvatarCropModal from '@/components/AvatarCropModal.vue'
import AboutModal from '@/components/profile/AboutModal.vue'
import SecurityModal from '@/components/profile/SecurityModal.vue'
import { ref } from 'vue'
import { getInitials } from '@/lib/utils'

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

const isAboutModalOpen = ref(false)
const isSecurityModalOpen = ref(false)

const isDark = useDark()
const toggleDark = useToggle(isDark)

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
              Editar Perfil
            </Button>
          </div>
        </CardContent>
      </Card>

      <div class="w-full">
        <Card class="border-border overflow-hidden">
          <div class="flex flex-col">
            <!-- Apariencia -->
            <button 
              class="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors border-b border-border text-left outline-none"
              @click="toggleDark()"
            >
              <div class="flex items-center gap-4">
                <div class="flex size-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <Palette class="size-5" />
                </div>
                <div>
                  <h3 class="font-medium text-foreground">Apariencia</h3>
                  <p class="text-xs text-muted-foreground">Cambiar modo claro / oscuro</p>
                </div>
              </div>
              <div class="flex items-center gap-2 text-muted-foreground">
                <Moon v-if="isDark" class="size-5" />
                <Sun v-else class="size-5" />
              </div>
            </button>

            <!-- Acerca de -->
            <button 
              class="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors border-b border-border text-left outline-none"
              @click="isAboutModalOpen = true"
            >
              <div class="flex items-center gap-4">
                <div class="flex size-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <HelpCircle class="size-5" />
                </div>
                <div>
                  <h3 class="font-medium text-foreground">Acerca de</h3>
                  <p class="text-xs text-muted-foreground">Preguntas frecuentes y guía rápida</p>
                </div>
              </div>
              <ChevronRight class="size-5 text-muted-foreground" />
            </button>

            <!-- Seguridad -->
            <button 
              class="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors border-b border-border text-left outline-none"
              @click="isSecurityModalOpen = true"
            >
              <div class="flex items-center gap-4">
                <div class="flex size-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
                  <ShieldCheck class="size-5" />
                </div>
                <div>
                  <h3 class="font-medium text-foreground">Seguridad</h3>
                  <p class="text-xs text-muted-foreground">Conoce cómo protegemos tus datos</p>
                </div>
              </div>
              <ChevronRight class="size-5 text-muted-foreground" />
            </button>

            <!-- Cerrar Sesión -->
            <button 
              class="flex items-center justify-between p-4 hover:bg-destructive/10 transition-colors text-left outline-none"
              @click="logout"
            >
              <div class="flex items-center gap-4">
                <div class="flex size-10 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                  <LogOut class="size-5" />
                </div>
                <div>
                  <h3 class="font-medium text-destructive">Cerrar Sesión</h3>
                  <p class="text-xs text-muted-foreground">Salir de tu cuenta de forma segura</p>
                </div>
              </div>
            </button>
          </div>
        </Card>
      </div>
    </div>
    <EditProfileModal v-model:open="isEditModalOpen" />
    <AvatarCropModal 
      v-model:open="isCropModalOpen" 
      :file="selectedFile" 
      @crop="handleCrop" 
    />
    <AboutModal v-model:open="isAboutModalOpen" />
    <SecurityModal v-model:open="isSecurityModalOpen" />
  </DashboardLayout>
</template>
