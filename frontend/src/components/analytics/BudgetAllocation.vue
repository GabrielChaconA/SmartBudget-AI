<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader>
      <CardTitle class="text-foreground">Budget Allocation (50/30/20)</CardTitle>
      <CardDescription>Actual vs target this month</CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <div class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium text-foreground">Needs (50%)</span>
          <span class="text-muted-foreground">46% of 50%</span>
        </div>
        <Progress :model-value="46" class="h-2 bg-muted/50 [&>div]:bg-success" />
      </div>
      
      <div class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium text-foreground">Wants (30%)</span>
          <span class="text-muted-foreground">34% of 30%</span>
        </div>
        <Progress :model-value="34" class="h-2 bg-muted/50 [&>div]:bg-success" />
      </div>

      <div class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium text-foreground">Savings (20%)</span>
          <span class="text-muted-foreground">20% of 20%</span>
        </div>
        <Progress :model-value="20" class="h-2 bg-muted/50 [&>div]:bg-success" />
      </div>
    </CardContent>
  </Card>
</template>
