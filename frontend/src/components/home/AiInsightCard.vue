<script setup lang="ts">
import { Sparkles } from '@lucide/vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { aiInsight } from '@/lib/data'
</script>

<template>
  <Card class="border-border">
    <CardContent class="flex flex-col gap-5 p-6 sm:p-8">
      <div class="flex items-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
          <Sparkles class="size-5" />
        </div>
        <div>
          <p class="text-sm font-semibold text-foreground">
            AI Insight
          </p>
          <p class="text-xs text-muted-foreground">
            Personalized recommendation
          </p>
        </div>
      </div>
      <p class="text-lg font-medium leading-relaxed text-foreground text-pretty">
        {{ aiInsight }}
      </p>
      <div class="flex flex-wrap gap-3">
        <Button>Apply suggestion</Button>
        <Button variant="outline">View details</Button>
      </div>
    </CardContent>
  </Card>
</template>
