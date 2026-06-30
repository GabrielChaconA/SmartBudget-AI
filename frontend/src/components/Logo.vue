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
    <div class="relative size-9 shrink-0 overflow-hidden rounded-xl bg-white ring-1 ring-border">
      <img
        src="/smartbudget-logo.png"
        alt="SmartBudget AI logo"
        class="pointer-events-none absolute max-w-none select-none"
        style="width: 328%; left: -22.8%; top: -42.8%"
      />
    </div>
    <span v-if="showWordmark" class="text-base font-semibold tracking-tight text-foreground">
      SmartBudget <span class="text-primary">AI</span>
    </span>
  </div>
</template>
