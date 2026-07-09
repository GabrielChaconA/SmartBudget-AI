<script setup lang="ts">
import { ref } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { ShieldCheck, Lock, Key, Server } from '@lucide/vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="props.open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <ShieldCheck class="size-5 text-primary" />
          Seguridad y Privacidad
        </DialogTitle>
        <DialogDescription>
          En SmartBudget, tu privacidad y la seguridad de tus datos son nuestra prioridad. Así es como protegemos tu información:
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col gap-6 py-4">
        
        <div class="flex gap-4">
          <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Lock class="size-5" />
          </div>
          <div>
            <h3 class="font-medium text-foreground">Cifrado de Datos Sensibles</h3>
            <p class="text-sm text-muted-foreground">Todos tus datos financieros viajan por internet utilizando protocolos de cifrado seguros (HTTPS/SSL). Nadie puede interceptar tu información mientras se transfiere.</p>
          </div>
        </div>

        <div class="flex gap-4">
          <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Key class="size-5" />
          </div>
          <div>
            <h3 class="font-medium text-foreground">Credenciales Protegidas</h3>
            <p class="text-sm text-muted-foreground">Tus contraseñas nunca se guardan en texto plano. Utilizamos algoritmos avanzados de "hashing" irreversibles, lo que significa que ni siquiera nosotros conocemos tu clave.</p>
          </div>
        </div>

        <div class="flex gap-4">
          <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Server class="size-5" />
          </div>
          <div>
            <h3 class="font-medium text-foreground">Sesiones Seguras</h3>
            <p class="text-sm text-muted-foreground">Tu cuenta utiliza un sistema moderno de tokens de autenticación (Sanctum) que expiran y previenen ataques de falsificación de peticiones.</p>
          </div>
        </div>

      </div>
    </DialogContent>
  </Dialog>
</template>
