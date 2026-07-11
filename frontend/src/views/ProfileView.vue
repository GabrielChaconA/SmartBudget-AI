<script setup lang="ts">

import { Pencil, Shield, LogOut, ChevronRight, Moon, Sun, HelpCircle, ShieldCheck, Palette, Globe } from '@lucide/vue'
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
import { useI18n } from 'vue-i18n'
import { useLocale, availableLocales, type Locale } from '@/composables/useLocale'

const { user, isLoading: isUserLoading, error: userError, uploadAvatar } = useUser()
const { logout } = useAuth()
const isEditModalOpen = ref(false)
const isCropModalOpen = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const { t } = useI18n()
const { locale, setLocale, currentLocale } = useLocale()

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
const isLanguagePickerOpen = ref(false)

const isDark = useDark()
const toggleDark = useToggle(isDark)

const selectLanguage = (code: Locale) => {
  setLocale(code)
  isLanguagePickerOpen.value = false
}

</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight text-foreground">
          {{ $t('profile.title') }}
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          {{ $t('profile.subtitle') }}
        </p>
      </div>

      <input type="file" accept="image/*" class="hidden" ref="fileInput" @change="handleFileChange" />

      <!-- Identity header -->
      <Card class="border-border min-h-[160px] flex flex-col justify-center">
        <CardContent v-if="isUserLoading" class="flex flex-col items-center justify-center py-6 text-muted-foreground">
          <Loader2 class="size-6 animate-spin mb-2" />
          <p>{{ $t('profile.loading') }}</p>
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
                {{ $t('profile.monthlyIncome') }} {{ formatCurrency(user.monthlyIncome, user.currency || 'USD') }}
              </p>
            </div>
          </div>
          <div class="flex flex-wrap justify-center gap-3">
            <Button class="bg-green-600 hover:bg-green-700 text-white" @click="isEditModalOpen = true">
              <Pencil class="mr-2 h-4 w-4" />
              {{ $t('profile.editProfile') }}
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
                  <h3 class="font-medium text-foreground">{{ $t('profile.appearance') }}</h3>
                  <p class="text-xs text-muted-foreground">{{ $t('profile.appearanceDesc') }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2 text-muted-foreground">
                <Moon v-if="isDark" class="size-5" />
                <Sun v-else class="size-5" />
              </div>
            </button>

            <!-- Idioma / Language -->
            <div class="border-b border-border">
              <button 
                class="flex w-full items-center justify-between p-4 hover:bg-muted/50 transition-colors text-left outline-none"
                @click="isLanguagePickerOpen = !isLanguagePickerOpen"
              >
                <div class="flex items-center gap-4">
                  <div class="flex size-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
                    <Globe class="size-5" />
                  </div>
                  <div>
                    <h3 class="font-medium text-foreground">{{ $t('profile.language') }}</h3>
                    <p class="text-xs text-muted-foreground">{{ $t('profile.languageDesc') }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2 text-muted-foreground">
                  <span class="text-sm font-medium">{{ currentLocale().flag }} {{ currentLocale().label }}</span>
                  <ChevronRight class="size-5 transition-transform" :class="isLanguagePickerOpen ? 'rotate-90' : ''" />
                </div>
              </button>

              <!-- Language picker inline -->
              <div v-if="isLanguagePickerOpen" class="flex flex-col border-t border-border bg-muted/30">
                <button
                  v-for="lang in availableLocales"
                  :key="lang.code"
                  class="flex items-center gap-3 px-6 py-3 text-left hover:bg-muted/50 transition-colors outline-none"
                  :class="locale === lang.code ? 'text-primary font-semibold' : 'text-foreground'"
                  @click="selectLanguage(lang.code)"
                >
                  <span class="text-xl">{{ lang.flag }}</span>
                  <span class="text-sm">{{ lang.label }}</span>
                  <span v-if="locale === lang.code" class="ml-auto text-primary text-xs">✓</span>
                </button>
              </div>
            </div>

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
                  <h3 class="font-medium text-foreground">{{ $t('profile.about') }}</h3>
                  <p class="text-xs text-muted-foreground">{{ $t('profile.aboutDesc') }}</p>
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
                  <h3 class="font-medium text-foreground">{{ $t('profile.security') }}</h3>
                  <p class="text-xs text-muted-foreground">{{ $t('profile.securityDesc') }}</p>
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
                  <h3 class="font-medium text-destructive">{{ $t('profile.logout') }}</h3>
                  <p class="text-xs text-muted-foreground">{{ $t('profile.logoutDesc') }}</p>
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
