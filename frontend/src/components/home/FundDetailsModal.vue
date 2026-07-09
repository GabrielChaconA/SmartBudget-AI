<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useUser } from '@/composables/useUser'
import { formatCurrency } from '@/lib/data'
import { Separator } from '@/components/ui/separator'
import { Pencil, Plus, Check, X, ArrowDownRight, ArrowUpRight, Trash2 } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  fund: any | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { updateFund, allocateFund, deleteAllocation, user, freeMoney } = useUser()

const isAddingAllocation = ref(false)
const allocName = ref('')
const allocIcon = ref('')
const allocAmount = ref(0)
const isSubmitting = ref(false)
const errorMessage = ref('')

// Transfer state
const transferMode = ref<'add' | 'withdraw'>('add')
const transferAmount = ref<number | ''>('')
const transferError = ref('')

// State for Sub-allocation selection
const selectedAllocation = ref<any | null>(null)

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    errorMessage.value = ''
    transferError.value = ''
    transferAmount.value = ''
    transferMode.value = 'add'
    selectedAllocation.value = null
  }
})

const totalAllocated = computed(() => {
  if (!props.fund?.allocations) return 0
  const sum = props.fund.allocations.reduce((sum: number, a: any) => sum + parseFloat(a.amount), 0)
  return Math.round(sum * 100) / 100
})

const fundFreeMoney = computed(() => {
  if (!props.fund) return 0
  const free = parseFloat(props.fund.balance) - totalAllocated.value
  return Math.round(free * 100) / 100
})

const maxTransferAmount = computed(() => {
  let max = 0
  if (selectedAllocation.value) {
    // We are transferring for a sub-allocation
    if (transferMode.value === 'add') {
      max = fundFreeMoney.value // Can only add up to what's free in the fund
    } else {
      max = parseFloat(selectedAllocation.value.amount) // Can only withdraw up to what's inside the sub-allocation
    }
  } else {
    // We are transferring for the main fund
    if (transferMode.value === 'add') {
      max = freeMoney.value // Can only add up to global free money
    } else {
      max = fundFreeMoney.value // Can only withdraw up to what's free in the fund
    }
  }
  return Math.round(max * 100) / 100
})

const handleTransfer = async () => {
  if (!props.fund || !transferAmount.value || Number(transferAmount.value) <= 0) return
  
  transferError.value = ''
  const amount = Number(transferAmount.value)

  if (amount > maxTransferAmount.value) {
    transferError.value = 'El monto supera el límite permitido para esta operación.'
    return
  }

  isSubmitting.value = true

  const roundedAmount = Math.round(amount * 100) / 100

  if (selectedAllocation.value) {
    // Sub-allocation transfer
    const currentAllocAmount = parseFloat(selectedAllocation.value.amount)
    const newAllocAmount = transferMode.value === 'add' ? currentAllocAmount + roundedAmount : currentAllocAmount - roundedAmount
    const roundedNewAlloc = Math.round(newAllocAmount * 100) / 100
    
    const success = await allocateFund(props.fund.id, selectedAllocation.value.category_name, roundedNewAlloc, selectedAllocation.value.category_icon || '')
    if (success) {
      transferAmount.value = ''
      // Update selected allocation amount locally to reflect immediately
      selectedAllocation.value.amount = roundedNewAlloc
    } else {
      transferError.value = 'Hubo un error al actualizar la sub-asignación.'
    }
  } else {
    // Main fund transfer
    const currentBalance = parseFloat(props.fund.balance)
    const newBalance = transferMode.value === 'add' ? currentBalance + roundedAmount : currentBalance - roundedAmount
    const roundedNewBalance = Math.round(newBalance * 100) / 100

    const success = await updateFund(props.fund.id, { balance: roundedNewBalance })
    if (success) {
      transferAmount.value = ''
    } else {
      transferError.value = 'Hubo un error al actualizar la caja.'
    }
  }
  
  isSubmitting.value = false
}

const handleAddAllocation = async () => {
  if (!props.fund || !allocName.value || allocAmount.value <= 0) return
  errorMessage.value = ''
  
  const roundedAmount = Math.round(allocAmount.value * 100) / 100

  if (roundedAmount > fundFreeMoney.value) {
    errorMessage.value = 'No tienes suficiente dinero libre en esta caja para esta operación.'
    return
  }

  isSubmitting.value = true
  const success = await allocateFund(props.fund.id, allocName.value, roundedAmount, allocIcon.value)
  if (success) {
    isAddingAllocation.value = false
    allocName.value = ''
    allocIcon.value = ''
    allocAmount.value = 0
  } else {
    errorMessage.value = 'Hubo un error al guardar la asignación.'
  }
  isSubmitting.value = false
}

const handleDeleteAllocation = async (alloc: any) => {
  if (!props.fund || !alloc.category_name) return
  isSubmitting.value = true
  errorMessage.value = ''
  const success = await deleteAllocation(props.fund.id, alloc.category_name)
  if (success && selectedAllocation.value?.category_name === alloc.category_name) {
    selectedAllocation.value = null
  } else if (!success) {
    errorMessage.value = 'Hubo un error al eliminar el sub-monto.'
  }
  isSubmitting.value = false
}

const toggleSelectAllocation = (alloc: any) => {
  if (selectedAllocation.value?.category_name === alloc.category_name) {
    selectedAllocation.value = null // Deselect
  } else {
    selectedAllocation.value = alloc
  }
  transferAmount.value = ''
  transferError.value = ''
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[900px] border-border/50">
      <DialogHeader>
        <DialogTitle class="text-2xl font-bold">{{ fund?.icon ? fund.icon + ' ' : '' }}{{ fund?.name || 'Caja' }}</DialogTitle>
        <DialogDescription class="text-muted-foreground">
          Gestiona el saldo de esta caja y sus sub-asignaciones internas.
        </DialogDescription>
      </DialogHeader>

      <div v-if="errorMessage" class="mt-4 p-3 text-sm rounded-md bg-destructive/15 text-destructive border border-destructive/20">
        {{ errorMessage }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 py-4" v-if="fund">
        
        <!-- Left Column: Fund Management -->
        <div class="space-y-6">
          <div class="rounded-xl border p-5 shadow-sm transition-colors cursor-pointer" 
               :class="!selectedAllocation ? 'bg-card border-primary ring-1 ring-primary' : 'bg-card/50 border-border hover:bg-card'"
               @click="selectedAllocation = null">
            <h3 class="text-sm font-medium" :class="!selectedAllocation ? 'text-primary' : 'text-muted-foreground'">Dinero Actual de la Caja</h3>
            
            <div class="mt-2">
              <p class="text-4xl font-bold tracking-tight text-foreground">{{ formatCurrency(fund.balance, user?.currency) }}</p>
              <p class="mt-2 text-xs font-medium text-muted-foreground flex items-center gap-1">
                Disponible para retirar / asignar: <span class="text-foreground font-bold">{{ formatCurrency(fundFreeMoney, user?.currency) }}</span>
              </p>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Sub-asignaciones</h3>
              <Button variant="outline" size="sm" class="h-7 gap-1 bg-muted border-border hover:bg-muted/80" @click="isAddingAllocation = true" v-if="!isAddingAllocation">
                <Plus class="size-3" /> Agregar
              </Button>
            </div>

            <div v-if="isAddingAllocation" class="flex flex-col gap-2 mb-4 p-3 rounded-lg border border-border bg-muted/50">
              <div class="flex items-end gap-2">
                <div class="w-12 space-y-1">
                  <Label class="text-[10px] uppercase tracking-wide text-muted-foreground">Icono</Label>
                  <Input v-model="allocIcon" placeholder="🛒" class="h-8 text-sm text-center px-1 bg-background border-border" maxlength="5" />
                </div>
                <div class="flex-1 space-y-1">
                  <Label class="text-[10px] uppercase tracking-wide text-muted-foreground">Categoría</Label>
                  <Input v-model="allocName" placeholder="Ej. Agua" class="h-8 text-sm bg-background border-border" />
                </div>
                <div class="w-32 space-y-1 relative">
                  <Label class="text-[10px] uppercase tracking-wide text-muted-foreground">Monto</Label>
                  <Input v-model="allocAmount" type="number" step="0.01" class="h-8 text-sm pr-10 bg-background border-border" />
                  <button class="absolute bottom-1 right-1 text-[10px] font-bold text-muted-foreground hover:text-foreground bg-muted px-1.5 py-0.5 rounded transition-colors" @click="allocAmount = Number(fundFreeMoney.toFixed(2))">MAX</button>
                </div>
                <Button size="sm" class="h-8 bg-primary hover:bg-primary/90 text-primary-foreground" @click="handleAddAllocation" :disabled="isSubmitting || !allocName || allocAmount <= 0">Guardar</Button>
                <Button size="sm" variant="ghost" class="h-8 px-2 text-muted-foreground hover:text-foreground hover:bg-muted" @click="isAddingAllocation = false">Cancelar</Button>
              </div>
              <p class="text-[11px] text-muted-foreground text-right mt-1">Disponible en caja: <span class="font-bold text-foreground">{{ formatCurrency(fundFreeMoney, user?.currency) }}</span></p>
            </div>

            <div class="space-y-2">
              <div v-for="(alloc, idx) in fund.allocations" :key="idx" 
                   class="flex items-center justify-between group cursor-pointer rounded-lg px-3 py-2 transition-colors border"
                   :class="selectedAllocation?.category_name === alloc.category_name ? 'bg-muted/80 border-primary/50' : 'bg-transparent border-transparent hover:bg-muted/30'"
                   @click="toggleSelectAllocation(alloc)">
                <p class="text-sm font-medium text-foreground/90"><span v-if="alloc.category_icon" class="mr-2">{{ alloc.category_icon }}</span>{{ alloc.category_name }}</p>
                
                <div class="flex items-center gap-3">
                  <p class="text-sm font-bold text-foreground">{{ formatCurrency(Number(alloc.amount), user?.currency) }}</p>
                  <Button size="icon" variant="ghost" class="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop="handleDeleteAllocation(alloc)">
                    <Trash2 class="size-3" />
                  </Button>
                </div>
              </div>
              <p v-if="!fund.allocations || fund.allocations.length === 0" class="text-sm text-muted-foreground text-center py-4 italic">
                No has agregado sub-asignaciones.
              </p>
              
              <Separator v-if="fund.allocations?.length > 0" class="my-3 border-border" />
              <div v-if="fund.allocations?.length > 0" class="flex justify-between items-center text-sm font-medium px-3">
                <span class="text-muted-foreground">Total Asignado:</span>
                <span class="text-foreground">{{ formatCurrency(totalAllocated, user?.currency) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Transfer Form -->
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-semibold tracking-tight text-foreground flex items-center gap-2">
              Transferir Dinero
              <span v-if="selectedAllocation" class="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">Modificando Sub-asignación</span>
            </h3>
            <p class="text-sm text-muted-foreground mt-1">
              {{ selectedAllocation 
                 ? `Agrega dinero a '${selectedAllocation.category_name}' desde tu caja, o retira dinero de esta asignación hacia la caja.` 
                 : 'Agrega dinero a esta caja desde tu dinero libre global, o retira dinero de esta caja hacia tu dinero libre.' }}
            </p>
          </div>
          
          <div class="rounded-xl border border-border bg-card p-5 shadow-sm relative overflow-hidden">
            <div v-if="selectedAllocation" class="absolute top-0 left-0 w-1 h-full bg-primary"></div>
            
            <div class="flex p-1 bg-muted/50 rounded-lg mb-6 border border-border">
              <button
                class="flex-1 py-2 text-sm font-medium rounded-md transition-all flex items-center justify-center gap-2"
                :class="transferMode === 'add' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground/80'"
                @click="transferMode = 'add'"
              >
                <ArrowDownRight class="size-4 text-green-500" />
                Ingresar
              </button>
              <button
                class="flex-1 py-2 text-sm font-medium rounded-md transition-all flex items-center justify-center gap-2"
                :class="transferMode === 'withdraw' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground/80'"
                @click="transferMode = 'withdraw'"
              >
                <ArrowUpRight class="size-4 text-destructive" />
                Retirar
              </button>
            </div>

            <div class="space-y-4">
              <div class="space-y-2">
                <Label class="text-xs uppercase tracking-wider text-muted-foreground font-bold">Monto a {{ transferMode === 'add' ? 'Ingresar' : 'Retirar' }}</Label>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground font-medium">$</span>
                  <Input 
                    type="number" 
                    step="0.01"
                    v-model="transferAmount" 
                    class="pl-7 h-12 text-lg font-semibold bg-background border-border focus-visible:ring-1 focus-visible:ring-primary/50" 
                    placeholder="0.00"
                  />
                  <button 
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] font-bold text-muted-foreground hover:text-foreground bg-muted px-2 py-1 rounded transition-colors" 
                    @click="transferAmount = Number(maxTransferAmount.toFixed(2))"
                  >
                    MÁXIMO
                  </button>
                </div>
                <div class="flex justify-between items-center text-xs mt-1.5">
                  <span class="text-muted-foreground">
                    {{ 
                      selectedAllocation 
                        ? (transferMode === 'add' ? 'Límite (Disponible en Caja):' : 'Límite (Retirar todo):')
                        : (transferMode === 'add' ? 'Límite (Tu Dinero Libre Global):' : 'Límite (Disponible en Caja):')
                    }}
                  </span>
                  <span class="font-semibold text-foreground/90">{{ formatCurrency(maxTransferAmount, user?.currency) }}</span>
                </div>
              </div>

              <div v-if="transferError" class="p-3 text-xs rounded-md bg-destructive/15 text-destructive border border-destructive/20">
                {{ transferError }}
              </div>

              <Button 
                class="w-full h-11 text-base font-semibold transition-all mt-4" 
                :class="transferMode === 'add' ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-red-600 hover:bg-red-700 text-white'"
                @click="handleTransfer"
                :disabled="isSubmitting || !transferAmount || Number(transferAmount) <= 0 || Number(transferAmount) > maxTransferAmount"
              >
                {{ isSubmitting ? 'Procesando...' : (transferMode === 'add' ? 'Confirmar Ingreso' : 'Confirmar Retiro') }}
              </Button>
            </div>
          </div>
        </div>

      </div>
    </DialogContent>
  </Dialog>
</template>
