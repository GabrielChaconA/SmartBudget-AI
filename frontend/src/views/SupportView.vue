<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, Wallet, TrendingUp, Sparkles, CreditCard, BarChart3 } from '@lucide/vue'
</script>

<template>
  <DashboardLayout>
    <div class="mx-auto max-w-4xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div class="text-center space-y-4">
        <h1 class="text-4xl font-extrabold tracking-tight">Bienvenido a SmartBudget AI</h1>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Tu centro de control financiero inteligente. Aquí tienes una guía rápida para aprovechar al máximo todas las herramientas y tomar el control de tu dinero.
        </p>
      </div>

      <div class="grid gap-6">
        <Card>
          <CardHeader class="pb-4">
            <CardTitle class="flex items-center gap-3 text-2xl">
              <Wallet class="size-6 text-primary" />
              1. Cajas (Funds) y Dinero Libre
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4 text-muted-foreground">
            <p>
              El corazón de tu presupuesto. En la pestaña de <strong>Home</strong> podrás visualizar tu dinero disponible.
            </p>
            <ul class="space-y-2 list-none">
              <li class="flex items-start gap-2">
                <CheckCircle2 class="size-5 text-green-500 shrink-0 mt-0.5" />
                <span><strong>Dinero Libre:</strong> Es el efectivo que tienes disponible para gastar en el día a día sin compromisos.</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle2 class="size-5 text-green-500 shrink-0 mt-0.5" />
                <span><strong>Cajas:</strong> Apartados específicos para tus metas (Ej. Viaje, Emergencias). El dinero aquí está protegido de tus gastos regulares.</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-4">
            <CardTitle class="flex items-center gap-3 text-2xl">
              <TrendingUp class="size-6 text-primary" />
              2. Inversiones en Tiempo Real
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4 text-muted-foreground">
            <p>
              Monitorea tu portafolio global en la pestaña de <strong>Investments</strong>. Todo se sincroniza automáticamente con los precios del mercado en vivo.
            </p>
            <ul class="space-y-2 list-none">
              <li class="flex items-start gap-2">
                <CheckCircle2 class="size-5 text-green-500 shrink-0 mt-0.5" />
                <span>Soporta múltiples activos: Acciones, ETFs, Criptomonedas y Apuestas deportivas.</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle2 class="size-5 text-green-500 shrink-0 mt-0.5" />
                <span>Conversión automática de divisas (MXN/USD) para darte tu Net Worth real al instante.</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-4">
            <CardTitle class="flex items-center gap-3 text-2xl">
              <CreditCard class="size-6 text-primary" />
              3. Gestión de Suscripciones
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4 text-muted-foreground">
            <p>
              En la sección de <strong>Memberships</strong> puedes llevar el control de tus pagos recurrentes (Netflix, Spotify, Gimnasio, etc.).
              Te ayudamos a visualizar cuánto de tu presupuesto mensual se destina a gastos fijos para que evites fugas de dinero.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-4">
            <CardTitle class="flex items-center gap-3 text-2xl">
              <BarChart3 class="size-6 text-primary" />
              4. Analytics
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4 text-muted-foreground">
            <p>
              Gráficas interactivas y hermosas que desglosan tu salud financiera. Podrás ver visualmente cómo está distribuido tu patrimonio total entre efectivo, inversiones y suscripciones, además del rendimiento histórico de tus mejores activos.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-4">
            <CardTitle class="flex items-center gap-3 text-2xl">
              <Sparkles class="size-6 text-primary" />
              5. Asistente AI (Chat)
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4 text-muted-foreground">
            <p>
              Un asesor financiero inteligente integrado directamente en tu app. Puedes preguntarle cosas como:
            </p>
            <ul class="space-y-2 list-none bg-muted/50 p-4 rounded-xl">
              <li class="italic text-sm">"¿Cuánto dinero me queda libre este mes si pago todas mis suscripciones?"</li>
              <li class="italic text-sm">"Analiza mi portafolio de inversiones y dime si estoy muy expuesto a criptomonedas."</li>
              <li class="italic text-sm">"¿Qué caja debería usar para comprar un nuevo monitor?"</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  </DashboardLayout>
</template>
