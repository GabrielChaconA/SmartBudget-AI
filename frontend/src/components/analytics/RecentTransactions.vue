<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Search } from '@lucide/vue'

const transactions = [
  { id: 1, date: 'Sep 15, 2025', merchant: 'Freelance Project', category: 'Income', account: 'Checking ••2210', amount: '+MX$7,800.00', type: 'income' },
  { id: 2, date: 'Sep 16, 2025', merchant: 'Soriana', category: 'Groceries', account: 'Debit ••4821', amount: '-MX$812.40', type: 'expense' },
  { id: 3, date: 'Sep 17, 2025', merchant: 'Spotify', category: 'Entertainment', account: 'Credit ••9013', amount: '-MX$129.00', type: 'expense' },
  { id: 4, date: 'Sep 18, 2025', merchant: 'Vanguard Transfer', category: 'Investment', account: 'Brokerage ••7740', amount: '-MX$5,000.00', type: 'expense' },
  { id: 5, date: 'Sep 19, 2025', merchant: 'CFE Electricity', category: 'Utilities', account: 'Checking ••2210', amount: '-MX$980.00', type: 'expense' },
  { id: 6, date: 'Sep 20, 2025', merchant: 'Starbucks', category: 'Restaurants', account: 'Debit ••4821', amount: '-MX$98.00', type: 'expense' },
  { id: 7, date: 'Sep 21, 2025', merchant: 'Amazon', category: 'Shopping', account: 'Credit ••9013', amount: '-MX$1,289.99', type: 'expense' },
  { id: 8, date: 'Sep 22, 2025', merchant: 'Uber', category: 'Transport', account: 'Credit ••9013', amount: '-MX$132.00', type: 'expense' },
  { id: 9, date: 'Sep 23, 2025', merchant: 'Salary Deposit', category: 'Income', account: 'Checking ••2210', amount: '+MX$25,500.00', type: 'income' },
  { id: 10, date: 'Sep 24, 2025', merchant: 'Rappi', category: 'Food', account: 'Debit ••4821', amount: '-MX$348.50', type: 'expense' },
]
</script>

<template>
  <Card class="bg-card border-border">
    <CardHeader class="flex flex-row items-start justify-between pb-4">
      <div>
        <CardTitle class="text-foreground">Recent Transactions</CardTitle>
        <CardDescription>Search, filter and sort your activity</CardDescription>
      </div>
      <div class="flex items-center gap-2">
        <div class="relative w-64">
          <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input type="text" placeholder="Search merchant..." class="pl-8 bg-transparent border-border" />
        </div>
        <Select defaultValue="all">
          <SelectTrigger class="w-[120px]">
            <SelectValue placeholder="All" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="income">Income</SelectItem>
            <SelectItem value="expenses">Expenses</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow class="hover:bg-transparent border-border">
            <TableHead class="w-[150px] text-foreground font-semibold">Date ↓↑</TableHead>
            <TableHead class="text-foreground font-semibold">Merchant</TableHead>
            <TableHead class="text-foreground font-semibold">Category</TableHead>
            <TableHead class="text-foreground font-semibold">Account</TableHead>
            <TableHead class="text-right text-foreground font-semibold">Amount ↑↓</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="transaction in transactions" :key="transaction.id" class="border-border/50 hover:bg-muted/30">
            <TableCell class="text-muted-foreground">{{ transaction.date }}</TableCell>
            <TableCell class="font-medium text-foreground">{{ transaction.merchant }}</TableCell>
            <TableCell>
              <Badge variant="outline" class="bg-muted/50 text-xs font-normal text-muted-foreground border-transparent">
                {{ transaction.category }}
              </Badge>
            </TableCell>
            <TableCell class="text-muted-foreground">{{ transaction.account }}</TableCell>
            <TableCell class="text-right font-semibold" :class="transaction.type === 'income' ? 'text-success' : 'text-foreground'">
              {{ transaction.amount }}
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</template>
