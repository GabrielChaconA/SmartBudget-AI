<script setup lang="ts">
import { cn } from "@/lib/utils"

withDefaults(defineProps<{
  class?: string
  showWordmark?: boolean
}>(), {
  showWordmark: true
})
</script>

<template>
  <div :class="cn('flex items-center gap-2.5', $props.class)">
    <span v-if="showWordmark" class="text-base font-semibold tracking-tight text-foreground">
      SmartBudget <span class="text-green-500">AI</span>
    </span>
  </div>
</template>
