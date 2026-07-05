<script setup lang="ts">
import { ref, computed } from 'vue'
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
import { formatCurrency } from '@/lib/data'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { createFund, freeMoney, user } = useUser()
const name = ref('')
const balance = ref(0)
const icon = ref('📦')
const isSubmitting = ref(false)

const isOverLimit = computed(() => balance.value > freeMoney.value)

const handleCreate = async () => {
  if (!name.value || balance.value < 0 || isOverLimit.value) return
  isSubmitting.value = true
  const success = await createFund({
    name: name.value,
    balance: balance.value,
    color: '#3b82f6', // Default blue
    icon: icon.value,
  })
  isSubmitting.value = false
  if (success) {
    name.value = ''
    balance.value = 0
    icon.value = '📦'
    emit('update:open', false)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Create New Fund</DialogTitle>
        <DialogDescription>
          Set up a new fund (caja) to track specific savings or expenses.
        </DialogDescription>
      </DialogHeader>
      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="icon" class="text-right">Icono (Emoji)</Label>
          <Input id="icon" v-model="icon" class="col-span-3 text-2xl h-12 w-16 text-center" placeholder="📦" maxlength="5" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="name" class="text-right">Name</Label>
          <Input id="name" v-model="name" class="col-span-3" placeholder="e.g., Vacation Fund" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="balance" class="text-right">Initial Balance</Label>
          <div class="col-span-3 space-y-1">
            <Input id="balance" type="number" v-model="balance" min="0" step="0.01" />
            <p v-if="isOverLimit" class="text-xs text-destructive">
              Cannot exceed free money ({{ formatCurrency(freeMoney, user?.currency) }})
            </p>
            <p v-else class="text-xs text-muted-foreground">
              Available free money: {{ formatCurrency(freeMoney, user?.currency) }}
            </p>
          </div>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button @click="handleCreate" :disabled="isSubmitting || !name || isOverLimit">Create Fund</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
