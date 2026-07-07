<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
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
import { exchangeRateService } from '@/services/exchangeRate'

const props = defineProps<{
  open: boolean
  initialCategory?: string
  defaultCurrency?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { addInvestment, user } = useUser()

const symbol = ref('')
const quantity = ref<number | ''>('')
const averagePrice = ref<number | ''>('')
const type = ref('etfs')
const currency = ref('MXN')
const isSubmitting = ref(false)

const exchangeRate = ref(20.0)

onMounted(async () => {
  exchangeRate.value = await exchangeRateService.getUsdMxnRate()
})

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    if (props.initialCategory) {
      type.value = props.initialCategory
    }
    if (props.defaultCurrency) {
      currency.value = props.defaultCurrency
    }
  }
})

const handleSave = async () => {
  if (!symbol.value || !quantity.value || !averagePrice.value || !type.value) return
  
  // Check if investment already exists
  const exists = user.value?.investments?.some((i: any) => i.symbol.toUpperCase() === symbol.value.toUpperCase())
  if (exists) {
    alert("Ya tienes esta inversión registrada. Usa la opción de compra/venta haciendo clic en ella desde la tabla principal.")
    return
  }

  // Calculate value in MXN for minimum validation
  let deduct_amount = Number(quantity.value) * Number(averagePrice.value)
  const userCurrency = user.value?.currency || 'MXN'
  if (currency.value === 'USD' && userCurrency === 'MXN') deduct_amount *= exchangeRate.value
  else if (currency.value === 'MXN' && userCurrency === 'USD') deduct_amount /= exchangeRate.value

  const valueInMxn = userCurrency === 'MXN' ? deduct_amount : deduct_amount * exchangeRate.value;
  if (valueInMxn < 20) {
    alert("El monto mínimo de inversión es de $20 MXN (o equivalente en USD).")
    return
  }

  isSubmitting.value = true

  const payload = {
    symbol: symbol.value.toUpperCase(),
    quantity: quantity.value,
    average_price: averagePrice.value, 
    currency: currency.value,
    type: type.value
  }

  const success = await addInvestment(payload)
  isSubmitting.value = false
  
  if (success) {
    symbol.value = ''
    quantity.value = ''
    averagePrice.value = ''
    type.value = 'etfs'
    currency.value = props.defaultCurrency || 'MXN'
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
            <Label>Number of Shares</Label>
            <Input type="number" v-model="quantity" placeholder="0.00" step="0.0001" />
          </div>
          <div class="space-y-2">
            <Label>Avg Price per Share</Label>
            <Input type="number" v-model="averagePrice" placeholder="0.00" step="0.01" />
          </div>
        </div>

        <div class="space-y-2">
          <Label>Currency</Label>
          <select v-model="currency" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
            <option value="MXN">Pesos (MXN)</option>
            <option value="USD">Dollars (USD)</option>
          </select>
        </div>

      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button 
          @click="handleSave" 
          :disabled="isSubmitting || !symbol || !quantity || !averagePrice"
          class="bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white rounded-lg h-8 px-4 text-xs font-semibold"
        >
          Save
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
