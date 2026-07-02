<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle, Search } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { fmpService } from '@/services/financialModelingPrep'
import { coingeckoService } from '@/services/coingecko'
import { oddsApiService } from '@/services/oddsApi'
import { formatCurrency } from '@/lib/data'

const route = useRoute()
const router = useRouter()
const category = computed(() => route.query.category as string || 'etfs')

const isLoading = ref(false)
const isError = ref(false)
const items = ref<any[]>([])
const lastUpdate = ref<Date | null>(null)
const searchQuery = ref('')
const showGainers = ref(true)
let pollInterval: ReturnType<typeof setInterval> | null = null

const fetchGainers = async () => {
  isLoading.value = true
  isError.value = false
  try {
    const type = showGainers.value ? 'gainers' : 'losers'
    if (category.value === 'etfs' || category.value === 'stocks') {
      const data = await fmpService.getMarketMovers(type)
      items.value = data.map((item: any) => ({
        id: item.symbol,
        name: item.name,
        ticker: item.symbol,
        price: item.price,
        changePct: item.changesPercentage,
        isPositive: item.changesPercentage >= 0
      })).slice(0, 20)
    } else if (category.value === 'crypto') {
      const data = await coingeckoService.getMarketMovers(type)
      items.value = data.map((item: any) => ({
        id: item.id,
        name: item.name,
        ticker: item.symbol.toUpperCase(),
        price: item.current_price,
        changePct: item.price_change_percentage_24h,
        isPositive: item.price_change_percentage_24h >= 0
      }))
    } else if (category.value === 'bets') {
      const data = await oddsApiService.getUpcomingOdds('upcoming', 20)
      items.value = data.map((item: any) => {
        const homeOdds = item.bookmakers?.[0]?.markets?.[0]?.outcomes?.[0]?.price || 1.0
        return {
          id: item.id,
          name: `${item.home_team} vs ${item.away_team}`,
          ticker: item.sport_title,
          price: homeOdds,
          changePct: 0,
          isPositive: true
        }
      })
      if (!showGainers.value) {
        items.value.reverse() // Just reverse for bets
      }
    }
  } catch (error) {
    console.error(error)
    isError.value = true
  } finally {
    isLoading.value = false
    lastUpdate.value = new Date()
  }
}

onMounted(() => {
  fetchGainers()
  // Poll every 30 seconds for real-time updates
  pollInterval = setInterval(fetchGainers, 30000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

const getCategoryName = (cat: string) => {
  switch(cat) {
    case 'etfs': return showGainers.value ? 'Top ETFs' : 'Bottom ETFs'
    case 'stocks': return showGainers.value ? 'Top Companies' : 'Bottom Companies'
    case 'crypto': return showGainers.value ? 'Top Crypto Gainers' : 'Top Crypto Losers'
    case 'bets': return 'Upcoming Bets'
    default: return 'Top Options'
  }
}

const filteredItems = computed(() => {
  if (!searchQuery.value) return items.value
  const query = searchQuery.value.toLowerCase()
  return items.value.filter(item => 
    item.name.toLowerCase().includes(query) || 
    item.ticker.toLowerCase().includes(query)
  )
})
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-4xl">
      <header class="pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <Button variant="outline" size="icon" @click="router.back()">
            <ArrowLeft class="size-4" />
          </Button>
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-foreground">
              {{ getCategoryName(category) }}
            </h1>
            <p class="mt-1 text-sm text-muted-foreground">
              Live updates of the top 20 options in the market.
            </p>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2">
          <div class="flex items-center gap-3">
            <span v-if="lastUpdate" class="text-xs text-muted-foreground animate-pulse">
              Last updated: {{ lastUpdate.toLocaleTimeString() }}
            </span>
            <Button variant="outline" size="sm" @click="fetchGainers" :disabled="isLoading">
              <RefreshCw class="size-4 mr-2" :class="{ 'animate-spin': isLoading }" />
              Refresh
            </Button>
          </div>
          <span v-if="isError" class="text-xs text-destructive flex items-center gap-1">
            <AlertCircle class="size-3" /> Error fetching live data
          </span>
        </div>
      </header>

      <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="relative w-full sm:max-w-sm">
          <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input 
            v-model="searchQuery" 
            placeholder="Search by name or ticker..." 
            class="pl-9 bg-card"
          />
        </div>
        <div class="flex items-center gap-3 bg-card px-4 py-2 rounded-lg border border-border" v-if="category !== 'bets'">
          <span class="text-sm font-medium cursor-pointer" :class="{ 'text-muted-foreground': showGainers }" @click="showGainers = false; fetchGainers()">
            Losers
          </span>
          
          <button 
            @click="showGainers = !showGainers; fetchGainers()"
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            :class="showGainers ? 'bg-green-500' : 'bg-red-500'"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-300 ease-in-out"
              :class="showGainers ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>

          <span class="text-sm font-medium cursor-pointer" :class="{ 'text-muted-foreground': !showGainers }" @click="showGainers = true; fetchGainers()">
            Gainers
          </span>
        </div>
      </div>

      <Card class="border-border">
        <CardContent class="divide-y divide-border p-0">
          <div v-if="filteredItems.length === 0 && !isLoading" class="p-8 text-center text-muted-foreground">
            No data available for this category or search query.
          </div>
          <div
            v-for="(h, index) in filteredItems"
            :key="h.id"
            class="flex items-center gap-4 px-4 py-4 sm:px-6 hover:bg-muted/30 transition-colors"
          >
            <span class="text-sm font-semibold text-muted-foreground w-6 text-center">
              {{ index + 1 }}
            </span>
            <span :class="[
              'flex size-10 items-center justify-center rounded-xl text-sm font-semibold shrink-0',
              h.isPositive ? 'bg-primary/15 text-primary' : 'bg-destructive/15 text-destructive'
            ]">
              <TrendingUp v-if="h.isPositive" class="size-5" />
              <TrendingDown v-else class="size-5" />
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium text-foreground">
                {{ h.name }}
              </p>
              <p class="text-sm text-muted-foreground">{{ h.ticker }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-foreground tabular-nums">
                {{ category === 'bets' ? h.price.toFixed(2) + 'x' : formatCurrency(h.price) }}
              </p>
              <div class="flex items-center justify-end gap-2" v-if="category !== 'bets'">
                <span :class="[
                  'inline-flex items-center gap-0.5 text-xs font-medium tabular-nums',
                  h.isPositive ? 'text-primary' : 'text-destructive'
                ]">
                  <ArrowUpRight v-if="h.isPositive" class="size-3.5" />
                  <ArrowDownRight v-else class="size-3.5" />
                  {{ h.isPositive ? '+' : '' }}{{ h.changePct.toFixed(2) }}%
                </span>
                <span class="text-xs text-muted-foreground">24h</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </DashboardLayout>
</template>
