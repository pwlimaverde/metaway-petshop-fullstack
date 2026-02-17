<script setup lang="ts">
import { onMounted, ref } from 'vue'

import Icon from '@/components/ui/Icon.vue'
import Avatar from '@/components/ui/Avatar.vue'
import { useAuthStore } from '@/stores/auth'
import { useClients } from '@/composables/useClients'
import type { Client } from '@/types/entities'

const authStore = useAuthStore()
const clientsApi = useClients()

const client = ref<Client | null>(null)

// Mock data (pode ser substituído por chamadas reais à API depois)
const counters = ref({
  pets: 0,
  nextAppointment: null as string | null,
})

const quickLinks = [
  { label: 'Meus Pets', to: '/my-pets', icon: 'PawPrint', description: 'Veja seus pets cadastrados' },
  { label: 'Agendamentos', to: '/my-appointments', icon: 'CalendarRange', description: 'Histórico e futuros' },
  { label: 'Meu Perfil', to: '/profile', icon: 'User', description: 'Seus dados pessoais' },
]

onMounted(async () => {
    // Carregar dados do cliente (foto, nome completo)
    try {
      client.value = await clientsApi.getMe()
    } catch (error) {
      console.error('Failed to load client profile', error)
    }

    // Futuramente: carregar contadores reais da API
    counters.value.pets = 2 // Exemplo
    counters.value.nextAppointment = 'Hoje, 14:00' // Exemplo
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
           <Avatar 
             :src="client?.photo_url" 
             :name="client?.name ?? authStore.user?.name" 
             size="md" 
             class="ring-2 ring-white/20 shadow-lg"
           />
           <p class="text-xs font-bold uppercase tracking-widest text-secondary-200 text-shadow-sm">Área do Cliente</p>
        </div>
        
        <h2 class="mb-4 font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Olá, <span class="text-transparent bg-clip-text bg-gradient-to-r from-secondary-400 to-primary-300">{{ authStore.user?.name?.split(' ')[0] ?? 'Cliente' }}</span>!
        </h2>
        <p class="max-w-xl text-lg text-neutral-400 leading-relaxed">
          Que bom te ver por aqui. Cuidamos com carinho de quem você ama.
        </p>
        
        <div class="mt-8 flex gap-4">
          <RouterLink to="/my-appointments" class="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-neutral-900 shadow-lg shadow-white/10 transition-transform hover:scale-105 hover:bg-neutral-50 active:scale-95">
            <Icon name="CalendarRange" :size="18" />
            Ver Agendamentos
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Quick Actions Grid -->
    <div class="mt-12">
      <div class="mb-6 flex items-center justify-between">
        <h3 class="font-display text-xl font-bold text-neutral-900">Acesso Rápido</h3>
      </div>
      
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="link in quickLinks"
          :key="link.to"
          :to="link.to"
          class="group flex items-center gap-4 rounded-2xl border border-neutral-100 bg-white p-5 shadow-sm transition-all duration-200 hover:border-secondary-200 hover:bg-secondary-50/30 hover:shadow-lg hover:shadow-secondary-900/5 cursor-pointer"
        >
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-neutral-50 text-neutral-400 transition-all group-hover:bg-secondary-100 group-hover:text-secondary-600 group-hover:scale-110">
             <Icon :name="link.icon" :size="20" />
          </div>
          <div class="flex-1">
            <p class="font-bold text-neutral-900 group-hover:text-secondary-700 transition-colors">{{ link.label }}</p>
            <p class="text-xs text-neutral-500 group-hover:text-secondary-600/70">{{ link.description }}</p>
          </div>
          <Icon name="ChevronRight" :size="16" class="ml-auto text-neutral-300 transition-transform group-hover:translate-x-1 group-hover:text-secondary-400" />
        </RouterLink>
      </div>
    </div>
  </section>
</template>
