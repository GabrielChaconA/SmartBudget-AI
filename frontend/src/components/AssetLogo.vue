<script setup lang="ts">
import { computed } from 'vue'
import { getAssetLogo } from '@/utils/assetLogos'

const props = defineProps<{
  symbol: string
  fallbackIcon?: any // Lucide icon component or similar
}>()

const logoData = computed(() => getAssetLogo(props.symbol))
</script>

<template>
  <template v-if="logoData">
    <svg 
      role="img" 
      viewBox="0 0 24 24" 
      xmlns="http://www.w3.org/2000/svg"
      class="size-5"
      :style="{ fill: '#' + logoData.hex }"
    >
      <title>{{ logoData.title }}</title>
      <path :d="logoData.path" />
    </svg>
  </template>
  <template v-else-if="fallbackIcon">
    <component :is="fallbackIcon" class="size-5" />
  </template>
</template>
