<script setup lang="ts">
import { ref } from 'vue'
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
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { createFund } = useUser()
const name = ref('')
const balance = ref(0)
const isSubmitting = ref(false)

const handleCreate = async () => {
  if (!name.value || balance.value < 0) return
  isSubmitting.value = true
  const success = await createFund({
    name: name.value,
    balance: balance.value,
    color: '#3b82f6', // Default blue
  })
  isSubmitting.value = false
  if (success) {
    name.value = ''
    balance.value = 0
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
          <Label for="name" class="text-right">Name</Label>
          <Input id="name" v-model="name" class="col-span-3" placeholder="e.g., Vacation Fund" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="balance" class="text-right">Initial Balance</Label>
          <Input id="balance" type="number" v-model="balance" class="col-span-3" min="0" step="0.01" />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button @click="handleCreate" :disabled="isSubmitting || !name">Create Fund</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
