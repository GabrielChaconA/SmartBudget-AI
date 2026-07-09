<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
</script>

<template>
  <div class="p-6 bg-card rounded-xl border border-border">
    <div class="flex flex-wrap items-end gap-4">
      <div class="space-y-1 w-40">
        <Label class="text-xs text-muted-foreground">Date Range</Label>
        <Select defaultValue="last-6-months">
          <SelectTrigger>
            <SelectValue placeholder="Select range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="last-3-months">Last 3 months</SelectItem>
            <SelectItem value="last-6-months">Last 6 months</SelectItem>
            <SelectItem value="last-year">Last year</SelectItem>
            <SelectItem value="ytd">Year to date</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div class="space-y-1 w-40">
        <Label class="text-xs text-muted-foreground">Category</Label>
        <Select defaultValue="all">
          <SelectTrigger>
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            <SelectItem value="housing">Housing</SelectItem>
            <SelectItem value="food">Food</SelectItem>
            <SelectItem value="transport">Transport</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div class="space-y-1 w-40">
        <Label class="text-xs text-muted-foreground">Account</Label>
        <Select defaultValue="all">
          <SelectTrigger>
            <SelectValue placeholder="Select account" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All accounts</SelectItem>
            <SelectItem value="checking">Checking</SelectItem>
            <SelectItem value="savings">Savings</SelectItem>
            <SelectItem value="credit">Credit Card</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="space-y-1 w-40">
        <Label class="text-xs text-muted-foreground">Income vs Expenses</Label>
        <Select defaultValue="both">
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="both">Both</SelectItem>
            <SelectItem value="income">Income Only</SelectItem>
            <SelectItem value="expenses">Expenses Only</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="space-y-1 w-40">
        <Label class="text-xs text-muted-foreground">Investment Account</Label>
        <Select defaultValue="all">
          <SelectTrigger>
            <SelectValue placeholder="Select account" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All investments</SelectItem>
            <SelectItem value="brokerage">Brokerage</SelectItem>
            <SelectItem value="crypto">Crypto Wallet</SelectItem>
            <SelectItem value="retirement">401(k)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="flex items-center gap-2">
        <Button class="bg-primary text-foreground hover:bg-primary/80">Apply</Button>
        <Button variant="ghost">Reset</Button>
      </div>
    </div>
  </div>
</template>
