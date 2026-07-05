<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useUser } from '@/composables/useUser'

const props = defineProps<{
  open: boolean
  initialCategory?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { addInvestment } = useUser()

const symbol = ref('')
const amount = ref<number | ''>('')
const type = ref('etfs')
const currency = ref('MXN')
const isSubmitting = ref(false)

watch(() => props.open, (isOpen) => {
  if (isOpen && props.initialCategory) {
    type.value = props.initialCategory
  }
})

const handleSave = async () => {
  if (!symbol.value || !amount.value || !type.value) return
  isSubmitting.value = true
  
  const payload = {
    symbol: symbol.value.toUpperCase(),
    quantity: amount.value,
    average_price: 1, 
    currency: currency.value,
    type: type.value,
  }

  const success = await addInvestment(payload)
  isSubmitting.value = false
  
  if (success) {
    symbol.value = ''
    amount.value = ''
    type.value = 'etfs'
    currency.value = 'MXN'
    emit('update:open', false)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Add Investment</DialogTitle>
        <DialogDescription>
          Record a new investment.
        </DialogDescription>
      </DialogHeader>
      
      <div class="grid gap-4 py-4">
        
        <div class="space-y-2" v-if="!initialCategory">
          <Label>Type</Label>
          <select v-model="type" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
            <option value="etfs">ETF</option>
            <option value="stocks">Company (Stock)</option>
            <option value="crypto">Cryptocurrency</option>
            <option value="bets">Bet</option>
          </select>
        </div>

        <div class="space-y-2">
          <Label>Symbol / Ticker</Label>
          <Input 
            v-model="symbol" 
            placeholder="e.g., VOO, AAPL, BTC..." 
            autocomplete="off"
            class="uppercase"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Total Invested</Label>
            <Input type="number" v-model="amount" placeholder="0.00" step="0.01" />
          </div>
          <div class="space-y-2">
            <Label>Currency</Label>
            <select v-model="currency" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
              <option value="MXN">Pesos (MXN)</option>
              <option value="USD">Dollars (USD)</option>
            </select>
          </div>
        </div>

      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button 
          @click="handleSave" 
          :disabled="isSubmitting || !symbol || !amount"
          class="bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white rounded-lg h-8 px-4 text-xs font-semibold"
        >
          Save
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
