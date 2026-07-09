<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { ChevronDown } from '@lucide/vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="props.open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[600px] max-h-[85vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Acerca de SmartBudget</DialogTitle>
        <DialogDescription>
          Guía rápida sobre cómo utilizar las diferentes secciones de la aplicación.
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col gap-4 py-4">
        
        <details class="group border-b border-border pb-4" open>
          <summary class="flex cursor-pointer items-center justify-between font-medium text-foreground outline-none list-none marker:hidden">
            Dashboard y Analytics
            <ChevronDown class="size-4 transition-transform group-open:rotate-180" />
          </summary>
          <p class="mt-3 text-sm text-muted-foreground leading-relaxed">
            El <strong>Dashboard (Home)</strong> te da un resumen general rápido de tu situación financiera actual. Puedes ver tu patrimonio neto, tu dinero libre y las inversiones. En la pestaña de <strong>Analytics</strong>, encontrarás gráficas detalladas para analizar el flujo de tus ingresos, en qué categorías gastas más y cómo se reparte tu riqueza total.
          </p>
        </details>
        
        <details class="group border-b border-border pb-4">
          <summary class="flex cursor-pointer items-center justify-between font-medium text-foreground outline-none list-none marker:hidden">
            Registrar Transacciones
            <ChevronDown class="size-4 transition-transform group-open:rotate-180" />
          </summary>
          <p class="mt-3 text-sm text-muted-foreground leading-relaxed">
            Desde la pantalla principal puedes usar el botón de <strong>Transacción</strong> para registrar cualquier ingreso (depositar a tus cuentas) o egreso (pagos o retiros). Esto ajustará automáticamente el saldo de la cuenta que selecciones y actualizará las gráficas.
          </p>
        </details>
        
        <details class="group border-b border-border pb-4">
          <summary class="flex cursor-pointer items-center justify-between font-medium text-foreground outline-none list-none marker:hidden">
            Membresías (Suscripciones)
            <ChevronDown class="size-4 transition-transform group-open:rotate-180" />
          </summary>
          <p class="mt-3 text-sm text-muted-foreground leading-relaxed">
            Aquí puedes registrar servicios que pagas de forma recurrente, como Netflix, Spotify o el gimnasio. SmartBudget calculará tu próxima fecha de pago real y el costo mensual total de todas tus membresías. En el Home te recordaremos cuáles están próximas a cobrarse.
          </p>
        </details>
        
        <details class="group border-b border-border pb-4">
          <summary class="flex cursor-pointer items-center justify-between font-medium text-foreground outline-none list-none marker:hidden">
            Inversiones
            <ChevronDown class="size-4 transition-transform group-open:rotate-180" />
          </summary>
          <p class="mt-3 text-sm text-muted-foreground leading-relaxed">
            Si compras ETFs, Acciones o Criptomonedas, puedes llevar el registro aquí. Te mostraremos un gráfico del crecimiento de tus inversiones a lo largo del tiempo, así como el rendimiento del día de hoy y el rendimiento histórico total.
          </p>
        </details>
        
        <details class="group pb-2">
          <summary class="flex cursor-pointer items-center justify-between font-medium text-foreground outline-none list-none marker:hidden">
            Cajas Globales (Goals)
            <ChevronDown class="size-4 transition-transform group-open:rotate-180" />
          </summary>
          <p class="mt-3 text-sm text-muted-foreground leading-relaxed">
            ¿Ahorrando para un viaje o un enganche? Puedes crear Cajas o Metas para guardar dinero. El dinero que asignes a estas cajas <strong>ya no aparecerá en tu saldo "Libre"</strong>, lo que te ayudará psicológicamente a no gastar los fondos reservados. Aún así, tu patrimonio neto seguirá contemplando ese dinero guardado.
          </p>
        </details>

      </div>
    </DialogContent>
  </Dialog>
</template>
