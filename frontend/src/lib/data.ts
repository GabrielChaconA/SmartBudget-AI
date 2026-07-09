// Mock data for SmartBudget AI. In a real app this would come from an API.

export const user = {
  name: "Mariana López",
  email: "mariana.lopez@gmail.com",
  avatar: "/avatars/mariana.png",
  currency: "MXN",
  monthlyIncome: 48000,
}

export const netWorth = {
  total: 152430.52,
  changePercent: 2.35,
  changeAmount: 1250,
}

export const summaryCards = [
  { id: "cash", title: "Available Cash", value: 34210.0, change: 1.2 },
  { id: "expenses", title: "Monthly Expenses", value: 18940.5, change: -3.4 },
  { id: "savings", title: "Monthly Savings", value: 9600.0, change: 5.8 },
  { id: "upcoming", title: "Upcoming Payments", value: 4320.0, change: 0 },
]

export const upcomingPayments = [
  { id: "netflix", name: "Netflix", when: "Tomorrow", amount: 219, category: "Entertainment" },
  { id: "spotify", name: "Spotify", when: "Friday", amount: 129, category: "Entertainment" },
  { id: "electricity", name: "Electricity", when: "Next week", amount: 980, category: "Utilities" },
  { id: "rent", name: "Apartment Rent", when: "In 12 days", amount: 12500, category: "Housing" },
]

export const aiInsight =
  "You spent 23% more on restaurants this month compared to your average. Reducing this category by $800 would allow you to reach your savings goal two weeks earlier."

export const netWorthEvolution = [
  { month: "Jan", value: 121400 },
  { month: "Feb", value: 124800 },
  { month: "Mar", value: 129100 },
  { month: "Apr", value: 133600 },
  { month: "May", value: 138200 },
  { month: "Jun", value: 141900 },
  { month: "Jul", value: 145300 },
  { month: "Aug", value: 148100 },
  { month: "Sep", value: 152430 },
]

export const incomeVsExpenses = [
  { month: "Apr", income: 46000, expenses: 19200 },
  { month: "May", income: 48000, expenses: 20100 },
  { month: "Jun", income: 47500, expenses: 17800 },
  { month: "Jul", income: 49000, expenses: 21300 },
  { month: "Aug", income: 48000, expenses: 18600 },
  { month: "Sep", income: 51000, expenses: 18940 },
]

export const expenseDistribution = [
  { category: "Housing", value: 12500, fill: "var(--chart-1)" },
  { category: "Food", value: 4200, fill: "var(--chart-2)" },
  { category: "Transport", value: 1800, fill: "var(--chart-3)" },
  { category: "Entertainment", value: 1240, fill: "var(--chart-4)" },
  { category: "Other", value: 980, fill: "var(--chart-5)" },
]

export const cashFlow = [
  { month: "Apr", flow: 26800 },
  { month: "May", flow: 27900 },
  { month: "Jun", flow: 29700 },
  { month: "Jul", flow: 27700 },
  { month: "Aug", flow: 29400 },
  { month: "Sep", flow: 32060 },
]

export const budgetAllocation = [
  { label: "Needs (50%)", target: 50, actual: 46 },
  { label: "Wants (30%)", target: 30, actual: 34 },
  { label: "Savings (20%)", target: 20, actual: 20 },
]

export const topSpending = [
  { category: "Rent", value: 12500, fill: "var(--chart-1)" },
  { category: "Groceries", value: 3100, fill: "var(--chart-2)" },
  { category: "Restaurants", value: 2400, fill: "var(--chart-3)" },
  { category: "Transport", value: 1800, fill: "var(--chart-4)" },
  { category: "Subscriptions", value: 760, fill: "var(--chart-5)" },
]

export const investmentAllocation = [
  { asset: "Stocks", value: 48, fill: "var(--chart-1)" },
  { asset: "ETFs", value: 27, fill: "var(--chart-2)" },
  { asset: "Crypto", value: 13, fill: "var(--chart-3)" },
  { asset: "Bonds", value: 12, fill: "var(--chart-4)" },
]

export const savingsRate = [
  { month: "Apr", rate: 16 },
  { month: "May", rate: 18 },
  { month: "Jun", rate: 21 },
  { month: "Jul", rate: 19 },
  { month: "Aug", rate: 22 },
  { month: "Sep", rate: 24 },
]

export const transactions = [
  { id: 1, date: "Sep 24, 2025", merchant: "Rappi", category: "Food", account: "Debit ••4821", amount: -348.5 },
  { id: 2, date: "Sep 23, 2025", merchant: "Salary Deposit", category: "Income", account: "Checking ••2210", amount: 25500 },
  { id: 3, date: "Sep 22, 2025", merchant: "Uber", category: "Transport", account: "Credit ••9013", amount: -132.0 },
  { id: 4, date: "Sep 21, 2025", merchant: "Amazon", category: "Shopping", account: "Credit ••9013", amount: -1289.99 },
  { id: 5, date: "Sep 20, 2025", merchant: "Starbucks", category: "Restaurants", account: "Debit ••4821", amount: -98.0 },
  { id: 6, date: "Sep 19, 2025", merchant: "CFE Electricity", category: "Utilities", account: "Checking ••2210", amount: -980.0 },
  { id: 7, date: "Sep 18, 2025", merchant: "Vanguard Transfer", category: "Investment", account: "Brokerage ••7740", amount: -5000 },
  { id: 8, date: "Sep 17, 2025", merchant: "Spotify", category: "Entertainment", account: "Credit ••9013", amount: -129.0 },
  { id: 9, date: "Sep 16, 2025", merchant: "Soriana", category: "Groceries", account: "Debit ••4821", amount: -812.4 },
  { id: 10, date: "Sep 15, 2025", merchant: "Freelance Project", category: "Income", account: "Checking ••2210", amount: 7800 },
]

export const linkedAccounts = [
  { id: 1, name: "BBVA Checking", type: "Checking", number: "••2210", balance: 34210.0 },
  { id: 2, name: "Santander Credit", type: "Credit", number: "••9013", balance: -8420.5 },
  { id: 3, name: "Nu Debit", type: "Debit", number: "••4821", balance: 12100.0 },
]

export const investmentAccounts = [
  { id: 1, name: "Vanguard Brokerage", type: "Brokerage", number: "••7740", balance: 96420.0 },
  { id: 2, name: "Bitso Crypto", type: "Crypto", number: "••3387", balance: 18120.0 },
]

export const memberships = [
  {
    id: "netflix",
    name: "Netflix",
    plan: "Premium 4K",
    amount: 219,
    cycle: "Monthly",
    nextCharge: "Oct 1, 2025",
    category: "Entertainment",
    active: true,
    notify: true,
  },
  {
    id: "spotify",
    name: "Spotify",
    plan: "Family",
    amount: 169,
    cycle: "Monthly",
    nextCharge: "Oct 3, 2025",
    category: "Entertainment",
    active: true,
    notify: true,
  },
  {
    id: "icloud",
    name: "iCloud+",
    plan: "200 GB",
    amount: 49,
    cycle: "Monthly",
    nextCharge: "Oct 8, 2025",
    category: "Storage",
    active: true,
    notify: false,
  },
  {
    id: "gym",
    name: "Smart Fit",
    plan: "Black",
    amount: 599,
    cycle: "Monthly",
    nextCharge: "Oct 10, 2025",
    category: "Health",
    active: true,
    notify: true,
  },
  {
    id: "chatgpt",
    name: "ChatGPT Plus",
    plan: "Pro",
    amount: 380,
    cycle: "Monthly",
    nextCharge: "Oct 12, 2025",
    category: "Productivity",
    active: true,
    notify: false,
  },
  {
    id: "amazon",
    name: "Amazon Prime",
    plan: "Annual",
    amount: 1790,
    cycle: "Yearly",
    nextCharge: "Mar 4, 2026",
    category: "Shopping",
    active: true,
    notify: true,
  },
  {
    id: "disney",
    name: "Disney+",
    plan: "Standard",
    amount: 159,
    cycle: "Monthly",
    nextCharge: "Cancelled",
    category: "Entertainment",
    active: false,
    notify: false,
  },
  {
    id: "adobe",
    name: "Adobe CC",
    plan: "Photography",
    amount: 219,
    cycle: "Monthly",
    nextCharge: "Paused",
    category: "Productivity",
    active: false,
    notify: false,
  },
]

export const investmentsSummary = {
  totalValue: 132680.45,
  investedAmount: 108400,
  totalReturnPercent: 22.4,
  dayChangePercent: 1.18,
}

export const portfolioPerformance = [
  { month: "Apr", value: 104200 },
  { month: "May", value: 109800 },
  { month: "Jun", value: 107300 },
  { month: "Jul", value: 118600 },
  { month: "Aug", value: 124100 },
  { month: "Sep", value: 132680 },
]

export interface InvestmentCategory {
  id: string;
  label: string;
  icon: string;
  value: number;
  returnPercent: number;
  dayPercent: number;
}

export interface InvestmentHolding {
  id: string
  name: string
  ticker: string
  value: number
  originalValue: number
  originalCurrency: string
  created_at?: string
  returnPercent: number
  dayPercent?: number
  totalInvestedNative?: number
};


export const investmentCategories = [
  { id: "etfs", label: "ETFs", icon: "etf", value: 41200, returnPercent: 14.2, dayPercent: 0.62 },
  { id: "stocks", label: "Empresas", icon: "company", value: 52800, returnPercent: 26.8, dayPercent: 1.45 },
  { id: "crypto", label: "Criptos", icon: "crypto", value: 24680, returnPercent: 38.1, dayPercent: 2.9 },
  { id: "bets", label: "Apuestas", icon: "bet", value: 14000, returnPercent: -8.4, dayPercent: -1.7 },
]

export const investmentHoldings = {
  etfs: [
    { id: "vti", name: "Vanguard Total Market", ticker: "VTI", value: 18400, returnPercent: 12.6, dayPercent: 0.4 },
    { id: "voo", name: "S&P 500 ETF", ticker: "VOO", value: 14200, returnPercent: 15.9, dayPercent: 0.7 },
    { id: "qqq", name: "Invesco Nasdaq 100", ticker: "QQQ", value: 8600, returnPercent: 18.3, dayPercent: 1.1 },
  ],
  stocks: [
    { id: "aapl", name: "Apple Inc.", ticker: "AAPL", value: 16800, returnPercent: 22.4, dayPercent: 0.9 },
    { id: "nvda", name: "NVIDIA Corp.", ticker: "NVDA", value: 21400, returnPercent: 64.1, dayPercent: 2.8 },
    { id: "msft", name: "Microsoft", ticker: "MSFT", value: 9200, returnPercent: 11.7, dayPercent: 0.5 },
    { id: "tsla", name: "Tesla Inc.", ticker: "TSLA", value: 5400, returnPercent: -6.2, dayPercent: -1.3 },
  ],
  crypto: [
    { id: "btc", name: "Bitcoin", ticker: "BTC", value: 13200, returnPercent: 42.6, dayPercent: 3.2 },
    { id: "eth", name: "Ethereum", ticker: "ETH", value: 7800, returnPercent: 31.4, dayPercent: 2.1 },
    { id: "sol", name: "Solana", ticker: "SOL", value: 3680, returnPercent: 28.9, dayPercent: 4.4 },
  ],
  bets: [
    { id: "champ", name: "Champions League Final", ticker: "FOOTBALL", value: 6000, returnPercent: 12.0, dayPercent: 0 },
    { id: "f1", name: "F1 Constructors Title", ticker: "F1", value: 4500, returnPercent: -22.5, dayPercent: -4.0 },
    { id: "nba", name: "NBA Finals MVP", ticker: "NBA", value: 3500, returnPercent: -14.3, dayPercent: -2.2 },
  ],
}

export const aiChatStarters = [
  "How much did I spend on subscriptions this month?",
  "Can I afford a $1,500 purchase right now?",
  "Where can I cut expenses to save more?",
  "Summarize my spending this week.",
]

export const aiInitialMessages = [
  {
    id: "m1",
    role: "assistant" as const,
    content:
      "Hi Mariana! I'm your SmartBudget assistant. Ask me anything about your spending, savings, or memberships.",
  },
]

export function formatCurrency(value: number, currency = "MXN") {
  let maxDigits = 2
  let minDigits = 2

  // For very small values (like crypto prices), show more decimals
  if (Math.abs(value) > 0 && Math.abs(value) < 1) {
    maxDigits = 6
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: minDigits,
    maximumFractionDigits: maxDigits,
  }).format(value)
}
