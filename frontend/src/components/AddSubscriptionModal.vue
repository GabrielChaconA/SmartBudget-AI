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
import { Switch } from '@/components/ui/switch'
import { useUser } from '@/composables/useUser'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { searchSubscriptionCatalog, addSubscription } = useUser()

const searchQuery = ref('')
const searchResults = ref<any[]>([])
const showDropdown = ref(false)
const selectedService = ref<any>(null)

const amount = ref<number | ''>('')
const nextBillingDate = ref('')
const notify = ref(true)
const isSubmitting = ref(false)

// Debounce logic for search
let timeout: any = null
watch(searchQuery, (newVal) => {
  if (selectedService.value && selectedService.value.name === newVal) {
    // If the query matches the selected service, don't search again
    return
  }
  selectedService.value = null // reset selection if user types something else

  clearTimeout(timeout)
  if (!newVal.trim()) {
    searchResults.value = []
    showDropdown.value = false
    return
  }

  timeout = setTimeout(async () => {
    searchResults.value = await searchSubscriptionCatalog(newVal)
    showDropdown.value = true
  }, 300)
})

const selectService = (service: any) => {
  selectedService.value = service
  searchQuery.value = service.name
  showDropdown.value = false
}

const handleSave = async () => {
  if (!searchQuery.value || !amount.value || !nextBillingDate.value) return
  isSubmitting.value = true
  
  const payload = {
    name: searchQuery.value,
    amount: amount.value,
    billing_cycle: 'monthly',
    next_billing_date: nextBillingDate.value,
    category_id: selectedService.value ? null : null, // Future use if needed
  }

  const success = await addSubscription(payload)
  isSubmitting.value = false
  
  if (success) {
    searchQuery.value = ''
    amount.value = ''
    nextBillingDate.value = ''
    notify.value = true
    selectedService.value = null
    emit('update:open', false)
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="sm:max-w-[425px] overflow-visible">
      <DialogHeader>
        <DialogTitle>Add Subscription</DialogTitle>
        <DialogDescription>
          Search for a service or type a custom one.
        </DialogDescription>
      </DialogHeader>
      
      <div class="grid gap-4 py-4">
        
        <!-- Searchable Dropdown -->
        <div class="space-y-2 relative">
          <Label>Service Name</Label>
          <Input 
            v-model="searchQuery" 
            placeholder="e.g., Netflix, Spotify..." 
            @focus="searchResults.length > 0 && (showDropdown = true)"
            autocomplete="off"
          />
          <!-- Dropdown items -->
          <ul 
            v-if="showDropdown && searchResults.length > 0" 
            class="absolute z-50 w-full mt-1 max-h-48 overflow-auto rounded-md border border-border bg-popover text-popover-foreground shadow-md"
          >
            <li 
              v-for="service in searchResults" 
              :key="service.id"
              class="relative flex w-full cursor-default select-none items-center rounded-sm py-2 px-3 text-sm outline-none hover:bg-accent hover:text-accent-foreground"
              @click="selectService(service)"
            >
              {{ service.name }}
            </li>
          </ul>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Amount</Label>
            <Input type="number" v-model="amount" placeholder="0.00" step="0.01" />
          </div>
          <div class="space-y-2">
            <Label>Next Billing Date</Label>
            <Input type="date" v-model="nextBillingDate" />
          </div>
        </div>

        <div class="flex flex-row items-center justify-between rounded-lg border border-border p-3 mt-2">
          <div class="space-y-0.5">
            <Label class="text-xs uppercase tracking-wide">Notify 24h Before Renewal</Label>
          </div>
          <Switch v-model:checked="notify" class="data-[state=checked]:bg-green-500" />
        </div>

      </div>
      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Cancel</Button>
        <Button @click="handleSave" :disabled="isSubmitting || !searchQuery || !amount || !nextBillingDate">Save</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
