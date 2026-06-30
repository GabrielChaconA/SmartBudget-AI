<script setup lang="ts">
import { ref, onUpdated, nextTick } from 'vue'
import { Sparkles, ArrowUp, User as UserIcon } from '@lucide/vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { aiChatStarters, aiInitialMessages, user } from '@/lib/data'

type Message = { id: string; role: 'assistant' | 'user'; content: string }

const cannedReplies: Record<string, string> = {
  subscriptions: "You have 6 active memberships totaling $1,615/month. Netflix and Spotify are your largest entertainment costs. Cancelling Disney+ already saved you $159/month.",
  afford: "Yes — with $34,210 in available cash and $9,600 in monthly savings, a $1,500 purchase keeps you comfortably above your safety buffer. It would push this month's savings rate to about 21%.",
  cut: "Your restaurants category is 23% above average this month. Trimming it by $800 and pausing Adobe CC ($219) would free up roughly $1,019/month toward your savings goal.",
  week: "This week you spent $1,710 across 9 transactions. The biggest were Amazon ($1,290) and groceries at Soriana ($812). You're still on track for your monthly budget.",
}

function getReply(input: string): string {
  const text = input.toLowerCase()
  if (text.includes("subscrip") || text.includes("member")) return cannedReplies.subscriptions
  if (text.includes("afford") || text.includes("buy") || text.includes("$")) return cannedReplies.afford
  if (text.includes("cut") || text.includes("save") || text.includes("reduce")) return cannedReplies.cut
  if (text.includes("week") || text.includes("summar")) return cannedReplies.week
  return "Based on your accounts, your finances look healthy this month with a 24% savings rate. Ask me about your spending, subscriptions, or savings goals for a detailed breakdown."
}

const messages = ref<Message[]>(aiInitialMessages)
const input = ref('')
const thinking = ref(false)
const scrollContainer = ref<HTMLDivElement | null>(null)

function scrollToBottom() {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTo({ top: scrollContainer.value.scrollHeight, behavior: 'smooth' })
  }
}

onUpdated(() => {
  scrollToBottom()
})

function send(text: string) {
  const trimmed = text.trim()
  if (!trimmed || thinking.value) return
  
  messages.value.push({ id: crypto.randomUUID(), role: 'user', content: trimmed })
  input.value = ''
  thinking.value = true
  
  setTimeout(() => {
    messages.value.push({ id: crypto.randomUUID(), role: 'assistant', content: getReply(trimmed) })
    thinking.value = false
    nextTick(scrollToBottom)
  }, 900)
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send(input.value)
  }
}
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto flex h-[calc(100vh-9.5rem)] max-w-3xl flex-col lg:h-[calc(100vh-7rem)]">
      <header class="flex items-center gap-3 pb-4">
        <span class="flex size-10 items-center justify-center rounded-xl bg-primary/15 text-primary">
          <Sparkles class="size-5" />
        </span>
        <div>
          <h1 class="text-lg font-semibold tracking-tight text-foreground">AI Assistant</h1>
          <p class="text-sm text-muted-foreground">Your personal finance copilot</p>
        </div>
      </header>

      <!-- Messages -->
      <div
        ref="scrollContainer"
        class="flex-1 space-y-5 overflow-y-auto rounded-2xl border border-border bg-card/40 p-4 sm:p-6"
      >
        <div
          v-for="m in messages"
          :key="m.id"
          :class="['flex items-start gap-3', m.role === 'user' ? 'flex-row-reverse' : '']"
        >
          <Avatar class="size-8 border border-border">
            <template v-if="m.role === 'user'">
              <AvatarImage v-if="user.avatar" :src="user.avatar" :alt="user.name" />
              <AvatarFallback>
                <UserIcon class="size-4" />
              </AvatarFallback>
            </template>
            <template v-else>
              <AvatarFallback class="bg-primary/15 text-primary">
                <Sparkles class="size-4" />
              </AvatarFallback>
            </template>
          </Avatar>
          <div
            :class="[
              'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
              m.role === 'user'
                ? 'rounded-tr-sm bg-primary text-primary-foreground'
                : 'rounded-tl-sm bg-muted text-foreground'
            ]"
          >
            {{ m.content }}
          </div>
        </div>

        <div v-if="thinking" class="flex items-center gap-3">
          <Avatar class="size-8 border border-border">
            <AvatarFallback class="bg-primary/15 text-primary">
              <Sparkles class="size-4" />
            </AvatarFallback>
          </Avatar>
          <div class="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
            <span class="size-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
            <span class="size-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
            <span class="size-2 animate-bounce rounded-full bg-muted-foreground" />
          </div>
        </div>
      </div>

      <!-- Suggested prompts -->
      <div v-if="messages.length <= 1" class="flex flex-wrap gap-2 pt-4">
        <Button
          v-for="s in aiChatStarters"
          :key="s"
          variant="outline"
          size="sm"
          class="rounded-full text-left"
          @click="send(s)"
        >
          {{ s }}
        </Button>
      </div>

      <!-- Composer -->
      <div class="pt-4">
        <div class="relative rounded-2xl border border-input bg-background overflow-hidden focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
          <textarea
            v-model="input"
            @keydown="handleKeyDown"
            placeholder="Ask about your spending, savings, or memberships…"
            class="min-h-12 w-full resize-none bg-transparent px-4 py-3 pb-12 text-sm outline-none placeholder:text-muted-foreground"
            rows="1"
          />
          <div class="absolute bottom-2 right-2">
            <Button
              class="rounded-full h-8 w-8 p-0"
              size="icon"
              :disabled="!input.trim() || thinking"
              @click="send(input)"
              aria-label="Send message"
            >
              <ArrowUp class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <p class="px-1 pt-2 text-center text-xs text-muted-foreground">
          SmartBudget AI can make mistakes. Verify important financial decisions.
        </p>
      </div>
    </div>
  </DashboardLayout>
</template>
