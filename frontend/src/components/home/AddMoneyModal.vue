<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Agregar Dinero Libre</DialogTitle>
        <DialogDescription>
          Ingresa la cantidad que deseas agregar a tu cuenta principal. Este dinero estará disponible para ser asignado a tus cajas.
        </DialogDescription>
      </DialogHeader>
      <div class="grid gap-4 py-4">
        <div v-if="errorMessage" class="p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
          {{ errorMessage }}
        </div>
        <div class="grid gap-2">
          <Label for="amount">Monto {{ user?.currency === 'USD' ? 'en USD' : 'en MXN' }}</Label>
          <Input id="amount" type="number" min="0.01" step="0.01" v-model="amount" placeholder="Ej. 5000" />
          <p v-if="user?.currency === 'USD' && exchangeRate" class="text-xs text-muted-foreground mt-1">
            ≈ {{ (Number(amount || 0) * exchangeRate).toLocaleString('en-US', { style: 'currency', currency: 'MXN' }) }} MXN (tasa: {{ exchangeRate.toFixed(2) }})
          </p>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancelar</Button>
        <Button @click="submit" :disabled="!amount || amount <= 0 || loading">
          <span v-if="loading">Agregando...</span>
          <span v-else>Agregar Dinero</span>
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
import { coingeckoService } from '@/services/coingecko';

const props = defineProps<{ open: boolean }>();
const emit = defineEmits<{ (e: 'update:open', value: boolean): void }>();

const amount = ref<number | ''>('');
const loading = ref(false);
const errorMessage = ref('');
const exchangeRate = ref(0);
const { addFreeMoney, user } = useUser();

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    amount.value = '';
    errorMessage.value = '';
    if (user.value?.currency === 'USD') {
      try {
        exchangeRate.value = await coingeckoService.getUsdMxnRate();
      } catch (e) {
        exchangeRate.value = 20.0;
      }
    }
  }
});

const submit = async () => {
  if (!amount.value || amount.value <= 0) return;
  loading.value = true;
  errorMessage.value = '';
  
  let finalAmount = Number(amount.value);
  if (user.value?.currency === 'USD' && exchangeRate.value > 0) {
    finalAmount *= exchangeRate.value;
  }
  
  const success = await addFreeMoney(finalAmount);
  loading.value = false;
  if (success) {
    emit('update:open', false);
  } else {
    errorMessage.value = 'Ocurrió un problema al agregar el dinero.';
  }
};
</script>
