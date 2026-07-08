<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
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
import { Trash2, TrendingUp, TrendingDown, Settings2 } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  investment: any
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { updateInvestment, deleteInvestment, user } = useUser()

const mode = ref<'buy'|'sell'|'edit'>('buy')

const symbol = ref('')
const quantity = ref<number | ''>('')
const averagePrice = ref<number | ''>('')
const type = ref('etfs')
const currency = ref('MXN')
const isSubmitting = ref(false)

const tradeQuantity = ref<number | ''>('')
const tradePrice = ref<number | ''>('')

const originalQuantity = ref<number>(0)
const originalAveragePrice = ref<number>(0)
const originalCurrency = ref('MXN')

const exchangeRate = ref(20.0)

onMounted(async () => {
  exchangeRate.value = await exchangeRateService.getUsdMxnRate()
})

watch(() => props.open, (isOpen) => {
  if (isOpen && props.investment) {
    symbol.value = props.investment.name || props.investment.symbol
    quantity.value = Number(props.investment.quantity) || 0
    averagePrice.value = Number(props.investment.average_price) || 0
    type.value = props.investment.type || 'etfs'
    currency.value = props.investment.currency || 'MXN'
    
    originalQuantity.value = Number(props.investment.quantity) || 0
    originalAveragePrice.value = Number(props.investment.average_price) || 0
    originalCurrency.value = props.investment.currency || 'MXN'
    
    tradeQuantity.value = ''
    tradePrice.value = ''
    mode.value = 'buy'
  }
})

const calculateBaseValue = (qty: number, price: number, cur: string) => {
  let res = qty * price
  const userCurrency = user.value?.currency || 'MXN'
  if (cur === 'USD' && userCurrency === 'MXN') {
    res *= exchangeRate.value
  } else if (cur === 'MXN' && userCurrency === 'USD') {
    res /= exchangeRate.value
  }
  return res
}

const checkMinimum = (val: number) => {
  const valueInMxn = (user.value?.currency === 'MXN') ? val : (val * exchangeRate.value);
  if (valueInMxn < 20) {
    alert("El monto mínimo de operación es de $20 MXN (o equivalente en USD).")
    return false
  }
  return true
}

const handleBuy = async () => {
  if (!tradeQuantity.value || !tradePrice.value) return
  
  const qtyToBuy = Number(tradeQuantity.value)
  const price = Number(tradePrice.value)
  
  const diff_amount = calculateBaseValue(qtyToBuy, price, originalCurrency.value)
  if (!checkMinimum(diff_amount)) return

  isSubmitting.value = true
  
  const currentQty = originalQuantity.value
  const currentAvgPrice = originalAveragePrice.value
  const newQty = currentQty + qtyToBuy
  const newAvgPrice = ((currentQty * currentAvgPrice) + (qtyToBuy * price)) / newQty

  const payload = {
    quantity: newQty,
    average_price: newAvgPrice
  }

  const success = await updateInvestment(props.investment.id, payload)
  isSubmitting.value = false
  if (success) emit('update:open', false)
}

const handleSell = async () => {
  if (!tradeQuantity.value || !tradePrice.value) return
  
  const qtyToSell = Number(tradeQuantity.value)
  const price = Number(tradePrice.value)
  
  const currentQty = originalQuantity.value
  if (qtyToSell > currentQty) {
    alert("No puedes vender más acciones de las que tienes.")
    return
  }
  
  const diff_amount = calculateBaseValue(qtyToSell, price, originalCurrency.value)
  
  isSubmitting.value = true
  const newQty = currentQty - qtyToSell

  if (newQty <= 0) {
    const success = await deleteInvestment(props.investment.id)
    isSubmitting.value = false
    if (success) emit('update:open', false)
    return
  }

  const payload = {
    quantity: newQty
  }

  const success = await updateInvestment(props.investment.id, payload)
  isSubmitting.value = false
  if (success) emit('update:open', false)
}

const handleEdit = async () => {
  if (!symbol.value || !quantity.value || !averagePrice.value || !type.value) return
  
  const currentBaseValue = calculateBaseValue(Number(quantity.value), Number(averagePrice.value), currency.value)
  if (!checkMinimum(currentBaseValue)) return

  isSubmitting.value = true
  
  const oldBaseValue = calculateBaseValue(originalQuantity.value, originalAveragePrice.value, originalCurrency.value)
  const diff_amount = currentBaseValue - oldBaseValue

  const payload = {
    symbol: symbol.value.toUpperCase(),
    quantity: quantity.value,
    average_price: averagePrice.value,
    currency: currency.value,
    type: type.value
  }

  const success = await updateInvestment(props.investment.id, payload)
  isSubmitting.value = false
  if (success) emit('update:open', false)
}

const submit = () => {
  if (mode.value === 'buy') handleBuy()
  else if (mode.value === 'sell') handleSell()
  else handleEdit()
}

const handleDelete = async () => {
  if (!confirm('¿Estás seguro de eliminar esta inversión?')) return;
  
  isSubmitting.value = true
  const success = await deleteInvestment(props.investment.id)
  isSubmitting.value = false
  if (success) emit('update:open', false)
}

const isSubmitDisabled = computed(() => {
  if (isSubmitting.value) return true
  if (mode.value === 'buy' || mode.value === 'sell') {
    return !tradeQuantity.value || !tradePrice.value
  }
  return !symbol.value || !quantity.value || !averagePrice.value
})
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Gestionar Inversión</DialogTitle>
        <DialogDescription>
          Opera tus posiciones de {{ symbol }}.
        </DialogDescription>
      </DialogHeader>
      
      <div class="flex items-center gap-1 p-1 bg-muted rounded-lg w-full mb-2">
        <button @click="mode = 'buy'" :class="mode === 'buy' ? 'bg-background shadow text-foreground' : 'text-muted-foreground'" class="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded-md transition-all">
          <TrendingUp class="size-3.5" /> Buy
        </button>
        <button @click="mode = 'sell'" :class="mode === 'sell' ? 'bg-background shadow text-foreground' : 'text-muted-foreground'" class="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded-md transition-all">
          <TrendingDown class="size-3.5" /> Sell
        </button>
        <button @click="mode = 'edit'" :class="mode === 'edit' ? 'bg-red-500 text-white shadow' : 'text-muted-foreground'" class="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded-md transition-all">
          <Settings2 class="size-3.5" /> Edit
        </button>
      </div>
      
      <!-- BUY/SELL FORM -->
      <div v-if="mode === 'buy' || mode === 'sell'" class="grid gap-4 py-2">
        <div class="p-3 bg-muted/50 rounded-lg border border-border">
          <p class="text-sm font-medium">Posición Actual</p>
          <div class="flex justify-between mt-1 text-xs text-muted-foreground">
            <span>Títulos: <strong class="text-foreground">{{ originalQuantity }}</strong></span>
            <span>Promedio: <strong class="text-foreground">${{ originalAveragePrice }} {{ originalCurrency }}</strong></span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Cantidad a {{ mode === 'buy' ? 'Comprar' : 'Vender' }}</Label>
            <Input type="number" v-model="tradeQuantity" placeholder="0.00" step="any" />
          </div>
          <div class="space-y-2">
            <Label>Precio de Operación</Label>
            <Input type="number" v-model="tradePrice" placeholder="0.00" step="any" />
          </div>
        </div>
        <p class="text-xs text-muted-foreground">La operación se registrará en la moneda original de esta inversión ({{ originalCurrency }}).</p>
      </div>

      <!-- EDIT FORM -->
      <div v-else class="grid gap-4 py-2">
        <div class="space-y-2">
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
          <Input v-model="symbol" placeholder="e.g., VOO, AAPL, BTC..." autocomplete="off" class="uppercase" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Number of Shares</Label>
            <Input type="number" v-model="quantity" placeholder="0.00" step="any" />
          </div>
          <div class="space-y-2">
            <Label>Avg Price per Share</Label>
            <Input type="number" v-model="averagePrice" placeholder="0.00" step="any" />
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

      <DialogFooter class="flex sm:justify-between items-center w-full mt-2">
        <Button v-if="mode === 'edit'" variant="ghost" class="text-red-500 hover:text-red-600 hover:bg-red-50 px-2" @click="handleDelete" :disabled="isSubmitting">
          <Trash2 class="size-4" />
        </Button>
        <div v-else></div>
        
        <div class="flex gap-2">
          <Button variant="outline" @click="$emit('update:open', false)">Cancelar</Button>
          <Button 
            @click="submit" 
            :disabled="isSubmitDisabled"
            :class="[
              'rounded-lg h-9 px-4 text-xs font-semibold text-white transition-colors',
              mode === 'buy' ? 'bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700' :
              mode === 'sell' ? 'bg-gradient-to-r from-orange-400 to-orange-600 hover:from-orange-500 hover:to-orange-700' :
              'bg-gradient-to-r from-red-500 to-red-700 hover:from-red-600 hover:to-red-800'
            ]"
          >
            {{ mode === 'buy' ? 'Registrar Compra' : mode === 'sell' ? 'Registrar Venta' : 'Guardar Cambios' }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
