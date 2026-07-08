<template>
  <Dialog :open="isOpen" @update:open="$emit('update:isOpen', $event)">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>Alertas de Precio: {{ holding?.symbol || holding?.ticker || holding?.name }}</DialogTitle>
        <DialogDescription>
          Recibe un correo electrónico cuando el precio cruce la meta indicada.
        </DialogDescription>
      </DialogHeader>
      
      <div class="py-4 space-y-6">
        <div>
          <h3 class="mb-3 text-sm font-medium text-foreground">Selecciona una meta rápida:</h3>
          <div class="grid grid-cols-3 gap-2">
            <Button variant="outline" size="sm" class="text-primary hover:text-primary hover:bg-primary/10" @click="setAlert(5)">
              +5%
            </Button>
            <Button variant="outline" size="sm" class="text-primary hover:text-primary hover:bg-primary/10" @click="setAlert(10)">
              +10%
            </Button>
            <Button variant="outline" size="sm" class="text-primary hover:text-primary hover:bg-primary/10" @click="setAlert(20)">
              +20%
            </Button>
            <Button variant="outline" size="sm" class="text-destructive hover:text-destructive hover:bg-destructive/10" @click="setAlert(-5)">
              -5%
            </Button>
            <Button variant="outline" size="sm" class="text-destructive hover:text-destructive hover:bg-destructive/10" @click="setAlert(-10)">
              -10%
            </Button>
            <Button variant="outline" size="sm" class="text-destructive hover:text-destructive hover:bg-destructive/10" @click="setAlert(-20)">
              -20%
            </Button>
          </div>
        </div>

        <div>
          <h3 class="mb-3 text-sm font-medium text-foreground">O ingresa un porcentaje personalizado:</h3>
          <div class="flex items-center gap-2">
            <div class="relative flex-1">
              <Input
                v-model="customPercent"
                type="number"
                placeholder="Ej. 15"
                class="pl-8"
              />
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
            </div>
            <Button @click="setAlert(Number(customPercent))" :disabled="!customPercent">
              Guardar Alerta
            </Button>
          </div>
        </div>
      </div>

      <DialogFooter class="sm:justify-start">
        <DialogClose as-child>
          <Button type="button" variant="secondary">
            Cerrar
          </Button>
        </DialogClose>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import axios from 'axios'

const props = defineProps<{
  isOpen: boolean
  holding: any
}>()

const emit = defineEmits(['update:isOpen'])

const customPercent = ref('')

const setAlert = async (percent: number) => {
  if (!percent || isNaN(percent)) return;
  
  try {
    const symbol = props.holding?.symbol || props.holding?.ticker || props.holding?.id;
    // Assuming backend will calculate target price based on current DB price
    await axios.post('/api/investment-alerts', {
      symbol: symbol,
      target_percent: percent,
    })
    
    alert(`Alerta Guardada: Te avisaremos cuando ${symbol} varíe un ${percent > 0 ? '+' : ''}${percent}%.`)
    
    emit('update:isOpen', false)
  } catch (error) {
    alert('Error: No se pudo guardar la alerta.')
  }
}
</script>
