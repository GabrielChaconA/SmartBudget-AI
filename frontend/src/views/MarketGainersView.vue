<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, RefreshCw, AlertCircle, Search, Trophy } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { fmpService } from '@/services/financialModelingPrep'
import { coingeckoService } from '@/services/coingecko'
import { oddsApiService, TOP_SPORTS, type OddsEvent } from '@/services/oddsApi'
import { apiSportsService } from '@/services/apiSports'
import { formatCurrency } from '@/lib/data'
import AssetLogo from '@/components/AssetLogo.vue'

const route = useRoute()
const router = useRouter()
const category = computed(() => route.query.category as string || 'etfs')

const isLoading = ref(false)
const isError = ref(false)
const items = ref<any[]>([])
const betsItems = ref<OddsEvent[]>([])
const teamLogos = ref<Record<string, string>>({})
const leagueLogos = ref<Record<string, string>>({})
const selectedSport = ref<string | null>(null)
const lastUpdate = ref<Date | null>(null)
const searchQuery = ref('')
const showGainers = ref(true)
const showBetaAlert = ref(false)
let pollInterval: ReturnType<typeof setInterval> | null = null

watch(category, (newCat) => {
  if (newCat === 'bets') {
    showBetaAlert.value = true
  }
})

const fetchGainers = async () => {
  if (category.value === 'bets' && !selectedSport.value) {
    // Phase 1: showing the sports grid, no API call needed.
    return
  }
  
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
    } else if (category.value === 'bets' && selectedSport.value) {
      betsItems.value = await oddsApiService.getUpcomingOdds(selectedSport.value, 40)
      
      // Fetch logos asynchronously
      betsItems.value.forEach(async (match) => {
         const sportKey = selectedSport.value!
         if (!teamLogos.value[match.home_team]) {
            const homeLogo = await apiSportsService.getTeamLogo(match.home_team, sportKey)
            if (homeLogo) teamLogos.value[match.home_team] = homeLogo
         }
         if (!teamLogos.value[match.away_team]) {
            const awayLogo = await apiSportsService.getTeamLogo(match.away_team, sportKey)
            if (awayLogo) teamLogos.value[match.away_team] = awayLogo
         }
      })
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
  pollInterval = setInterval(fetchGainers, 30000)
  
  if (category.value === 'bets') {
     showBetaAlert.value = true

     TOP_SPORTS.forEach(async (sport) => {
        const logo = await apiSportsService.getLeagueLogo(sport.title, sport.key)
        if (logo) leagueLogos.value[sport.key] = logo
     })
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

const getCategoryName = (cat: string) => {
  switch(cat) {
    case 'etfs': return showGainers.value ? 'Top ETFs' : 'Bottom ETFs'
    case 'stocks': return showGainers.value ? 'Top Companies' : 'Bottom Companies'
    case 'crypto': return showGainers.value ? 'Top Crypto Gainers' : 'Top Crypto Losers'
    case 'bets': 
      if (selectedSport.value) {
         return TOP_SPORTS.find(s => s.key === selectedSport.value)?.title || 'Bets'
      }
      return 'Top Sports'
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

const selectSport = (sportKey: string) => {
  selectedSport.value = sportKey
  betsItems.value = []
  fetchGainers()
}

const goBack = () => {
  if (category.value === 'bets' && selectedSport.value) {
    selectedSport.value = null
  } else {
    router.back()
  }
}
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-4xl">
      <header class="pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <Button variant="outline" size="icon" @click="goBack">
            <ArrowLeft class="size-4" />
          </Button>
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-foreground">
              {{ getCategoryName(category) }}
            </h1>
            <p class="mt-1 text-sm text-muted-foreground">
              {{ category === 'bets' && !selectedSport 
                 ? 'Select a sport to see upcoming betting odds.' 
                 : 'Live updates of the top options in the market.' }}
            </p>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2" v-if="!(category === 'bets' && !selectedSport)">
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

      <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4" v-if="category !== 'bets'">
        <div class="relative w-full sm:max-w-sm">
          <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input 
            v-model="searchQuery" 
            placeholder="Search by name or ticker..." 
            class="pl-9 bg-card"
          />
        </div>
        <div class="flex items-center gap-3 bg-card px-4 py-2 rounded-lg border border-border">
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

      <!-- BETS CATEGORY -->
      <template v-if="category === 'bets'">
        <!-- Phase 1: Sports Selection -->
        <div v-if="!selectedSport" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <Card 
            v-for="sport in TOP_SPORTS" 
            :key="sport.key"
            class="cursor-pointer hover:border-primary/50 transition-colors bg-card group"
            @click="selectSport(sport.key)"
          >
            <CardContent class="p-6 flex flex-col items-center justify-center text-center gap-3">
              <div class="size-12 rounded-full bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform overflow-hidden">
                <img v-if="leagueLogos[sport.key]" :src="leagueLogos[sport.key]" class="size-8 object-contain" />
                <Trophy v-else class="size-6" />
              </div>
              <div>
                <h3 class="font-semibold text-foreground">{{ sport.title }}</h3>
                <p class="text-xs text-muted-foreground mt-1">{{ sport.description }}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Phase 2: Matches & Odds -->
        <div v-else>
          <div v-if="isLoading" class="text-center py-12 text-muted-foreground">
            <RefreshCw class="size-8 animate-spin mx-auto mb-4" />
            <p>Loading upcoming matches...</p>
          </div>
          <div v-else-if="betsItems.length === 0" class="text-center py-12 text-muted-foreground">
            <p>No upcoming matches found for this sport.</p>
          </div>
          <div v-else class="grid gap-6">
            <Card v-for="match in betsItems" :key="match.id" class="border-border">
              <CardHeader class="bg-muted/30 pb-4">
                <div class="flex items-center justify-between">
                  <span class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                     <img v-if="selectedSport && leagueLogos[selectedSport]" :src="leagueLogos[selectedSport]" class="size-4 object-contain" />
                     <Trophy v-else class="size-3" />
                     {{ match.sport_title }}
                  </span>
                  <span class="text-xs text-muted-foreground">{{ new Date(match.commence_time).toLocaleString() }}</span>
                </div>
                <CardTitle class="flex items-center gap-4 mt-4">
                   <div class="flex-1 flex items-center justify-end gap-3 text-right">
                     <span class="text-lg font-bold">{{ match.home_team }}</span>
                     <img v-if="teamLogos[match.home_team]" :src="teamLogos[match.home_team]" alt="Logo" class="size-8 object-contain" />
                     <div v-else class="size-8 rounded-full overflow-hidden bg-primary/10 text-primary flex items-center justify-center font-bold text-xs shrink-0 border border-primary/20">
                        {{ match.home_team.substring(0,2).toUpperCase() }}
                     </div>
                   </div>
                   <div class="px-3 py-1 bg-muted rounded-md text-xs font-bold text-muted-foreground">VS</div>
                   <div class="flex-1 flex items-center justify-start gap-3 text-left">
                     <img v-if="teamLogos[match.away_team]" :src="teamLogos[match.away_team]" alt="Logo" class="size-8 object-contain" />
                     <div v-else class="size-8 rounded-full overflow-hidden bg-destructive/10 text-destructive flex items-center justify-center font-bold text-xs shrink-0 border border-destructive/20">
                        {{ match.away_team.substring(0,2).toUpperCase() }}
                     </div>
                     <span class="text-lg font-bold">{{ match.away_team }}</span>
                   </div>
                </CardTitle>
              </CardHeader>
              <CardContent class="p-0">
                <div v-if="!match.bookmakers || match.bookmakers.length === 0" class="p-4 text-center text-sm text-muted-foreground">
                  No odds available
                </div>
                <div v-else class="divide-y divide-border">
                   <div v-for="bookmaker in match.bookmakers" :key="bookmaker.title" class="flex flex-col sm:flex-row sm:items-center justify-between p-4 hover:bg-muted/10 transition-colors">
                     <div class="font-medium text-sm text-foreground mb-3 sm:mb-0 w-32 flex items-center gap-2">
                       <AssetLogo :symbol="bookmaker.title.substring(0,2).toUpperCase()" />
                       {{ bookmaker.title }}
                     </div>
                     <div class="flex gap-2 flex-wrap sm:flex-nowrap">
                       <div v-for="outcome in bookmaker.markets[0].outcomes" :key="outcome.name" class="bg-card border border-border rounded-md px-3 py-1.5 flex flex-col items-center min-w-[80px]">
                         <span class="text-[10px] text-muted-foreground uppercase truncate w-full text-center">{{ outcome.name === match.home_team ? 'Home' : (outcome.name === match.away_team ? 'Away' : 'Draw') }}</span>
                         <span class="font-bold text-sm tabular-nums text-foreground">{{ outcome.price.toFixed(2) }}</span>
                       </div>
                     </div>
                   </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </template>

      <!-- STANDARD CATEGORIES -->
      <Card class="border-border" v-else>
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
              'flex size-10 items-center justify-center rounded-xl text-sm font-semibold shrink-0 overflow-hidden',
              h.isPositive ? 'bg-primary/15 text-primary' : 'bg-destructive/15 text-destructive'
            ]">
              <AssetLogo :symbol="h.ticker" :fallback-icon="h.isPositive ? TrendingUp : TrendingDown" />
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium text-foreground">
                {{ h.name }}
              </p>
              <p class="text-sm text-muted-foreground">{{ h.ticker }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-foreground tabular-nums">
                {{ formatCurrency(h.price) }}
              </p>
              <div class="flex items-center justify-end gap-2">
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

    <!-- Beta Alert Dialog -->
    <Dialog v-model:open="showBetaAlert">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-destructive">
            <AlertCircle class="size-5" /> 
            Sección en Desarrollo (Fase Beta)
          </DialogTitle>
          <DialogDescription class="pt-2 text-base">
            La sección de <strong>Apuestas Deportivas</strong> se encuentra en fase de construcción. Puedes visualizar algunos campos de apuestas, equipos y momios (cuotas), pero aún estamos trabajando para implementar todas las funcionalidades (como apostar o ver resultados históricos).
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="destructive" @click="showBetaAlert = false">Entendido</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </DashboardLayout>
</template>
