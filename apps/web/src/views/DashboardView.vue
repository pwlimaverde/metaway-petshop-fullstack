<script setup lang="ts">
import { onMounted, ref } from 'vue'

import Card from '@/components/ui/Card.vue'
import Icon from '@/components/ui/Icon.vue'
import { useAppointments } from '@/composables/useAppointments'
import { useClients } from '@/composables/useClients'
import { usePets } from '@/composables/usePets'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const clientsApi = useClients()
const petsApi = usePets()
const appointmentsApi = useAppointments()

const counters = ref({ clients: 0, pets: 0, appointments: 0 })

const quickLinks = [
  { label: 'Gerenciar clientes', to: '/admin/clients' },
  { label: 'Gerenciar pets', to: '/admin/pets' },
  { label: 'Gerenciar atendimentos', to: '/admin/appointments' },
]

async function loadCounters() {
  try {
    const [clients, pets, appointments] = await Promise.all([
      clientsApi.list(),
      petsApi.list(),
      appointmentsApi.list(),
    ])
    counters.value = {
      clients: clients.length,
      pets: pets.length,
      appointments: appointments.length,
    }
  } catch {
    counters.value = { clients: 0, pets: 0, appointments: 0 }
  }
}

onMounted(() => {
  loadCounters()
})
</script>

<template>
  <section class="space-y-8">
    <!-- Hero Section / Welcome -->
    <div class="relative overflow-hidden rounded-3xl bg-neutral-900 px-8 py-10 shadow-2xl shadow-neutral-900/20 sm:px-12 sm:py-16 ring-1 ring-white/10">
      <!-- Rich Background (Consistent with Login) -->
      <div class="absolute inset-0 z-0">
        <img
          src="@/assets/hero-pets.png"
          alt="Background Pattern"
          class="h-full w-full object-cover object-[70%_35%] opacity-40 mix-blend-overlay grayscale-[20%]"
        />
        <!-- Gradient Overlays -->
        <div class="absolute inset-0 bg-gradient-to-r from-neutral-900/90 via-neutral-900/60 to-primary-900/20 mix-blend-multiply"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-neutral-900/60 via-transparent to-transparent"></div>
      </div>
      
      <div class="relative z-10">
        <div class="mb-4 flex items-center gap-3">
           <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 text-primary-400 backdrop-blur-md ring-1 ring-white/20 shadow-lg shadow-black/20">
             <Icon name="Sparkles" :size="16" />
           </div>
           <p class="text-xs font-bold uppercase tracking-widest text-primary-200 text-shadow-sm">Painel Administrativo</p>
        </div>
        
        <h2 class="mb-4 font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Olá, <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-secondary-300">{{ authStore.user?.name?.split(' ')[0] ?? 'Admin' }}</span>
        </h2>
        <p class="max-w-xl text-lg text-neutral-400 leading-relaxed">
          Aqui está o resumo do que está acontecendo no seu petshop hoje. Você tem <strong class="text-white">{{ counters.appointments }} atendimentos</strong> agendados.
        </p>
        
        <div class="mt-8 flex gap-4">
          <RouterLink to="/admin/appointments" class="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-neutral-900 shadow-lg shadow-white/10 transition-transform hover:scale-105 hover:bg-neutral-50 active:scale-95">
            <Icon name="Plus" :size="18" />
            Novo Agendamento
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid gap-6 md:grid-cols-3">
      <!-- Clients Card -->
      <Card variant="elevated" class="group relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-primary-900/5">
        <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-blue-50/50 transition-all group-hover:scale-110"></div>
        
        <div class="relative z-10 p-2">
          <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 shadow-sm ring-4 ring-blue-50/50 transition-colors group-hover:bg-blue-600 group-hover:text-white group-hover:ring-blue-200">
            <Icon name="Users" :size="26" />
          </div>
          <p class="text-sm font-medium text-neutral-500">Total de Clientes</p>
          <div class="mt-2 flex items-baseline justify-between">
            <p class="font-display text-4xl font-bold tracking-tight text-neutral-900">{{ counters.clients }}</p>
            <div class="flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 ring-1 ring-emerald-600/10">
              <Icon name="TrendingUp" :size="12" />
              <span>+12%</span>
            </div>
          </div>
        </div>
      </Card>

      <!-- Pets Card -->
      <Card variant="elevated" class="group relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-primary-900/5">
        <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary-50/50 transition-all group-hover:scale-110"></div>
        
        <div class="relative z-10 p-2">
          <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-50 text-primary-600 shadow-sm ring-4 ring-primary-50/50 transition-colors group-hover:bg-primary-600 group-hover:text-white group-hover:ring-primary-200">
             <Icon name="PawPrint" :size="26" />
          </div>
          <p class="text-sm font-medium text-neutral-500">Pets Cadastrados</p>
          <div class="mt-2 flex items-baseline justify-between">
            <p class="font-display text-4xl font-bold tracking-tight text-neutral-900">{{ counters.pets }}</p>
            <div class="flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 ring-1 ring-emerald-600/10">
              <Icon name="TrendingUp" :size="12" />
              <span>+5%</span>
            </div>
          </div>
        </div>
      </Card>

      <!-- Appts Card -->
      <Card variant="elevated" class="group relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-primary-900/5">
        <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-rose-50/50 transition-all group-hover:scale-110"></div>
        
        <div class="relative z-10 p-2">
          <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 shadow-sm ring-4 ring-rose-50/50 transition-colors group-hover:bg-rose-600 group-hover:text-white group-hover:ring-rose-200">
            <Icon name="CalendarRange" :size="26" />
          </div>
          <p class="text-sm font-medium text-neutral-500">Atendimentos Hoje</p>
           <div class="mt-2 flex items-baseline justify-between">
            <p class="font-display text-4xl font-bold tracking-tight text-neutral-900">{{ counters.appointments }}</p>
            <div class="flex items-center gap-1 rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-bold text-neutral-600 ring-1 ring-neutral-500/10">
              <span>Hoje</span>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Quick Actions -->
    <div>
      <div class="mb-6 flex items-center justify-between">
        <h3 class="font-display text-xl font-bold text-neutral-900">Acesso Rápido</h3>
        <button class="text-sm font-medium text-primary-600 hover:text-primary-700">Ver todos</button>
      </div>
      
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="link in quickLinks"
          :key="link.to"
          :to="link.to"
          class="group flex items-center gap-4 rounded-2xl border border-neutral-100 bg-white p-5 shadow-sm transition-all duration-200 hover:border-primary-200 hover:bg-primary-50/30 hover:shadow-lg hover:shadow-primary-900/5"
        >
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-neutral-50 text-neutral-400 transition-all group-hover:bg-primary-100 group-hover:text-primary-600 group-hover:scale-110">
             <Icon name="ArrowRight" :size="20" />
          </div>
          <div>
            <p class="font-bold text-neutral-900 group-hover:text-primary-700 transition-colors">{{ link.label }}</p>
            <p class="text-xs text-neutral-500 group-hover:text-primary-600/70">Gerenciar registros</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </section>
</template>
