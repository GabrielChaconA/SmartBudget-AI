<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Gestionar Dinero Libre</DialogTitle>
        <DialogDescription>
          Ingresa la cantidad que deseas agregar o quitar de tu cuenta principal (Cartera).
        </DialogDescription>
      </DialogHeader>
      <div class="grid gap-4 py-4">
        <div v-if="errorMessage" class="p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
          {{ errorMessage }}
        </div>
        
        <div class="flex items-center gap-1 p-1 bg-muted rounded-lg w-full mb-2">
          <button @click="mode = 'add'" :class="mode === 'add' ? 'bg-background shadow text-foreground' : 'text-muted-foreground'" class="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded-md transition-all">
            <PlusCircle class="size-3.5" /> Agregar
          </button>
          <button @click="mode = 'remove'" :class="mode === 'remove' ? 'bg-background shadow text-foreground' : 'text-muted-foreground'" class="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded-md transition-all">
            <MinusCircle class="size-3.5" /> Quitar
          </button>
        </div>

        <div class="grid gap-2">
          <div class="flex items-center justify-between">
            <Label for="amount">Monto {{ user?.currency === 'USD' ? 'en USD' : 'en MXN' }}</Label>
            <div v-if="mode === 'remove'" class="text-xs text-muted-foreground flex items-center gap-2">
              <span>Disponible: {{ formatAvailable() }}</span>
              <button @click="setMax" class="text-primary hover:underline font-medium cursor-pointer">Max</button>
            </div>
          </div>
          <Input id="amount" type="number" min="0.01" step="0.01" v-model="amount" placeholder="Ej. 5000" />
          <p v-if="user?.currency === 'USD' && exchangeRate" class="text-xs text-muted-foreground mt-1">
            ≈ {{ (Number(amount || 0) * exchangeRate).toLocaleString('en-US', { style: 'currency', currency: 'MXN' }) }} MXN (tasa: {{ exchangeRate.toFixed(2) }})
          </p>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancelar</Button>
        <Button @click="submit" :disabled="!amount || amount <= 0 || loading">
          <span v-if="loading">Procesando...</span>
          <span v-else>{{ mode === 'add' ? 'Agregar Dinero' : 'Quitar Dinero' }}</span>
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useUser } from '@/composables/useUser';
import { exchangeRateService } from '@/services/exchangeRate';
import { PlusCircle, MinusCircle } from '@lucide/vue'

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: 'update:open', value: boolean): void }>();

const amount = ref<number | ''>('');
const loading = ref(false);
const errorMessage = ref('');
const exchangeRate = ref(0);
const mode = ref<'add'|'remove'>('add');
const { addFreeMoney, user, freeMoney } = useUser();

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    amount.value = '';
    errorMessage.value = '';
    mode.value = 'add';
    if (user.value?.currency === 'USD') {
      try {
        exchangeRate.value = await exchangeRateService.getUsdMxnRate();
      } catch (e) {
        exchangeRate.value = 20.0;
      }
    }
  }
});

const formatAvailable = () => {
  let val = freeMoney.value;
  if (user.value?.currency === 'USD' && exchangeRate.value > 0) {
    val /= exchangeRate.value;
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: user.value?.currency || 'MXN' }).format(val);
}

const setMax = () => {
  let val = freeMoney.value;
  if (user.value?.currency === 'USD' && exchangeRate.value > 0) {
    val /= exchangeRate.value;
  }
  amount.value = Number(val.toFixed(2));
}

const submit = async () => {
  if (!amount.value || amount.value <= 0) return;
  loading.value = true;
  errorMessage.value = '';
  
  let finalAmount = Number(amount.value);
  if (user.value?.currency === 'USD' && exchangeRate.value > 0) {
    finalAmount *= exchangeRate.value;
  }
  
  if (mode.value === 'remove') {
    if (finalAmount > freeMoney.value + 0.01) { // 0.01 tolerance for floating point
      errorMessage.value = 'No puedes quitar más dinero del que tienes disponible.';
      loading.value = false;
      return;
    }
    finalAmount = -Math.abs(finalAmount);
  }
  
  const success = await addFreeMoney(finalAmount);
  loading.value = false;
  if (success) {
    emit('update:open', false);
  } else {
    errorMessage.value = 'Ocurrió un problema al procesar la operación.';
  }
};
</script>
