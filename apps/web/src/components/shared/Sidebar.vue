<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import Icon from '@/components/ui/Icon.vue'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()
const authStore = useAuthStore()

const adminLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
  { to: '/admin/clients', label: 'Clientes', icon: 'Users' },
  { to: '/admin/users', label: 'Usuários', icon: 'Shield' },
  { to: '/admin/breeds', label: 'Raças', icon: 'Tags' },
  { to: '/admin/pets', label: 'Pets', icon: 'PawPrint' },
  { to: '/admin/appointments', label: 'Atendimentos', icon: 'CalendarRange' },
] as const

const clientLinks = [
  { to: '/client-dashboard', label: 'Início', icon: 'LayoutDashboard' },
  { to: '/profile', label: 'Meu Perfil', icon: 'User' },
  { to: '/my-pets', label: 'Meus Pets', icon: 'PawPrint' },
  { to: '/my-appointments', label: 'Meus Atendimentos', icon: 'CalendarRange' },
] as const

const navLinks = computed(() => (authStore.isAdmin ? adminLinks : clientLinks))

function handleLinkClick() {
  if (window.innerWidth < 768) {
    emit('close')
  }
}
</script>

<template>
  <div class="relative flex h-full flex-col justify-between overflow-hidden rounded-3xl bg-neutral-900 shadow-2xl shadow-neutral-900/50 ring-1 ring-white/10">
    
    <!-- Rich Background (From AuthLayout) -->
    <div class="absolute inset-0 z-0">
       <img
        src="@/assets/hero-pets.png"
        alt="Background"
        class="h-full w-full object-cover opacity-20 mix-blend-overlay"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-neutral-900 via-neutral-900/90 to-primary-900/40 mix-blend-multiply"></div>
      <div class="absolute inset-0 bg-neutral-900/40 backdrop-blur-[2px]"></div>
    </div>

    <!-- Header / Logo -->
    <div class="relative z-10 flex h-24 items-center justify-between px-6 pt-4">
      <div class="flex items-center gap-4">
        <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-primary-400 shadow-lg shadow-black/20 ring-1 ring-white/20 backdrop-blur-md">
           <!-- Simple paw icon SVG - White/Primary -->
           <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 5.172C10 3.782 8.423 2.679 6.5 3c-2.823.47-4.113 4.912-5 7 .887 5.882 5.887 7 5 7 2.05-.005 3.5-1.618 3.5-3.5 0-1.882-1.118-3.5-3.5-3.5C6.5 10 5.5 10 5.5 10s-1 4.5 2.5 4.5c1.455.004 2.5-1.118 2.5-2.5V5.172z"/><path d="M14 5.172C14 3.782 15.577 2.679 17.5 3c2.823.47 4.113 4.912 5 7-.887 5.882-5.887 7-5 7-2.05-.005-3.5-1.618-3.5-3.5 0-1.882 1.118-3.5 3.5-3.5C17.5 10 18.5 10 18.5 10s1 4.5-2.5 4.5c-1.455.004-2.5-1.118-2.5-2.5V5.172z"/></svg>
        </div>
        <div>
          <p class="font-display text-lg font-bold tracking-tight text-white">Metaway</p>
          <p class="text-[10px] font-bold uppercase tracking-widest text-primary-400">Petshop</p>
        </div>
      </div>
      
      <!-- Close Button (Mobile Only) -->
      <button 
        @click="emit('close')"
        class="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 md:hidden"
      >
        <Icon name="X" :size="18" />
      </button>
    </div>

    <!-- Navigation -->
    <nav aria-label="Menu principal" class="relative z-10 flex-1 space-y-2 overflow-y-auto px-4 py-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-neutral-700">
      <p class="mb-3 px-4 text-[10px] font-bold uppercase tracking-widest text-neutral-500">Principal</p>
      <RouterLink
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        :aria-current="route.path === link.to ? 'page' : undefined"
        @click="handleLinkClick"
        class="group relative flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-300 overflow-hidden"
        :class="
          route.path === link.to
            ? 'bg-primary-500/10 text-primary-400 shadow-sm shadow-black/20 ring-1 ring-primary-500/20'
            : 'text-neutral-400 hover:bg-white/5 hover:text-white'
        "
      >
        <!-- Active Indicator (Glow) -->
        <div 
           v-if="route.path === link.to"
           class="absolute left-0 top-1/2 h-8 w-1 -translate-y-1/2 rounded-r-full bg-primary-400 shadow-[0_0_12px_rgba(45,212,191,0.6)]"
        ></div>

        <Icon
          :name="link.icon"
          :size="20"
          class="relative z-10 transition-transform duration-300 group-hover:scale-110"
          :class="route.path === link.to ? 'text-primary-400' : 'text-neutral-500 group-hover:text-white'"
        />
        <span class="relative z-10">{{ link.label }}</span>
      </RouterLink>
    </nav>
    
    <!-- Footer / User Profile -->
    <div class="relative z-10 p-4 pb-6">
      <div class="group flex items-center gap-3 rounded-2xl border border-transparent bg-white/5 p-3 transition-all duration-300 hover:border-white/10 hover:bg-white/10 hover:shadow-xl hover:shadow-black/20 cursor-pointer">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-neutral-700 to-neutral-800 text-sm font-bold text-white shadow-inner ring-1 ring-white/10">
          {{ authStore.user?.name?.substring(0,2).toUpperCase() ?? 'US' }}
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-bold text-white group-hover:text-primary-400 transition-colors">{{ authStore.user?.name ?? 'Usuário' }}</p>
          <p class="truncate text-xs font-medium text-neutral-500">Ver Perfil</p>
        </div>
        <Icon name="ChevronUp" :size="16" class="text-neutral-500 group-hover:text-primary-400 transition-colors" />
      </div>
    </div>
  </div>
</template>
