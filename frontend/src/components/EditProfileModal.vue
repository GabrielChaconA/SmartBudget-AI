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
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { user, updateProfile } = useUser()

const name = ref('')
const isSubmitting = ref(false)

// Initialize name when modal opens
watch(() => props.open, (isOpen) => {
  if (isOpen && user.value) {
    name.value = user.value.name || ''
  }
})

const handleSave = async () => {
  if (!name.value.trim()) return
  isSubmitting.value = true
  
  const success = await updateProfile({ name: name.value })
  isSubmitting.value = false
  
  if (success) {
    emit('update:open', false)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogDescription>
          Update your personal information.
        </DialogDescription>
      </DialogHeader>
      
      <div class="grid gap-4 py-4">
        <div class="space-y-2">
          <Label for="name">Name</Label>
          <Input 
            id="name"
            v-model="name" 
            placeholder="Your full name" 
            autocomplete="name"
          />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)" :disabled="isSubmitting">Cancel</Button>
        <Button @click="handleSave" :disabled="isSubmitting || !name.trim()" class="bg-green-600 hover:bg-green-700 text-white">Save Changes</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
