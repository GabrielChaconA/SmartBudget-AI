<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const props = defineProps<{
  open: boolean
  file: File | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'crop': [blob: Blob]
}>()

const cropper = ref<any>(null)
const imageSrc = ref<string | null>(null)
const isCropping = ref(false)

// Convert file to object URL
watch(() => props.file, (newFile) => {
  if (imageSrc.value) {
    URL.revokeObjectURL(imageSrc.value)
    imageSrc.value = null
  }
  if (newFile) {
    imageSrc.value = URL.createObjectURL(newFile)
  }
}, { immediate: true })

// Cleanup on unmount
onUnmounted(() => {
  if (imageSrc.value) {
    URL.revokeObjectURL(imageSrc.value)
  }
})

const handleOpenChange = (open: boolean) => {
  emit('update:open', open)
}

const cropAndSave = async () => {
  if (!cropper.value) return
  isCropping.value = true

  const { canvas } = cropper.value.getResult()
  if (canvas) {
    canvas.toBlob((blob: Blob | null) => {
      isCropping.value = false
      if (blob) {
        emit('crop', blob)
      }
    }, props.file?.type || 'image/jpeg')
  } else {
    isCropping.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-md bg-card border-border">
      <DialogHeader>
        <DialogTitle class="text-foreground">Adjust Profile Picture</DialogTitle>
        <DialogDescription>
          Drag and zoom to position your avatar.
        </DialogDescription>
      </DialogHeader>

      <div class="my-4 w-full h-[300px] bg-background/50 rounded-lg overflow-hidden flex items-center justify-center border border-border">
        <Cropper
          v-if="imageSrc"
          ref="cropper"
          class="cropper w-full h-full"
          :src="imageSrc"
          :stencil-props="{
            aspectRatio: 1
          }"
        />
        <div v-else class="text-muted-foreground text-sm">
          No image selected
        </div>
      </div>

      <DialogFooter class="sm:justify-between flex-row gap-2">
        <Button variant="outline" @click="handleOpenChange(false)">Cancel</Button>
        <Button @click="cropAndSave" :disabled="isCropping || !imageSrc">
          <span v-if="isCropping">Cropping...</span>
          <span v-else>Save Picture</span>
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.cropper {
  background: transparent;
}
</style>
