<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import Sidebar from '@/components/shared/Sidebar.vue'
import Button from '@/components/ui/Button.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const isSidebarOpen = ref(false)

const pageTitle = computed(() => {
  const titleMap: Record<string, string> = {
    '/dashboard': 'Dashboard',
    '/profile': 'Meu Perfil',
    '/my-addresses': 'Meus Endereços',
    '/my-contacts': 'Meus Contatos',
    '/my-pets': 'Meus Pets',
    '/my-appointments': 'Meus Atendimentos',
    '/admin/clients': 'Clientes',
    '/admin/users': 'Usuários',
    '/admin/breeds': 'Raças',
    '/admin/pets': 'Pets',
    '/admin/appointments': 'Atendimentos',
  }

  return titleMap[route.path] ?? 'Metaway Petshop'
})
</script>

<template>
  <div class="min-h-screen bg-neutral-50 font-sans selection:bg-primary-100 selection:text-primary-900">
    <!-- Background Decoration -->
    <!-- Background Decoration -->
    <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-neutral-50">
      <!-- Background Image -->
      <img
        src="@/assets/hero-pets.png"
        alt="Background Pattern"
        class="absolute inset-0 h-full w-full object-cover opacity-[0.03] mix-blend-multiply grayscale"
      />
      
      <!-- Decorative Blobs (reduced opacity) -->
      <div class="absolute -top-[20%] -left-[10%] h-[70%] w-[60%] rounded-full bg-primary-100/30 blur-[120px] mix-blend-multiply"></div>
      <div class="absolute top-[10%] -right-[10%] h-[60%] w-[50%] rounded-full bg-secondary-100/30 blur-[100px] mix-blend-multiply"></div>
    </div>

    <!-- Main Shell -->
    <div class="relative z-10 flex min-h-screen flex-col md:flex-row">
      
      <!-- Sidebar Wrapper (Floating) -->
      <aside 
        class="fixed inset-y-0 left-0 z-50 w-72 p-4 transition-transform duration-300 ease-out md:translate-x-0"
        :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <Sidebar :open="isSidebarOpen" @close="isSidebarOpen = false" />
      </aside>

      <!-- Overlay for Mobile Sidebar -->
      <div 
        v-if="isSidebarOpen" 
        class="fixed inset-0 z-40 bg-neutral-900/20 backdrop-blur-sm md:hidden" 
        @click="isSidebarOpen = false"
      ></div>

      <!-- Main Content Area -->
      <div class="flex-1 transition-all duration-300 ease-out md:ml-72">
        
        <!-- Header (Floating/Contextual) -->
        <header class="sticky top-0 z-30 px-6 py-4">
          <div class="mx-auto flex max-w-7xl items-center justify-between rounded-2xl bg-white/70 px-4 py-3 shadow-sm shadow-neutral-200/50 backdrop-blur-xl ring-1 ring-white/50 transition-all">
            
            <div class="flex items-center gap-3">
              <Button variant="ghost" size="sm" class="md:hidden text-neutral-500 hover:text-neutral-900 -ml-2" @click="isSidebarOpen = true">
                <span class="sr-only">Abrir menu</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
              </Button>
              
              <div class="flex flex-col">
                <h1 class="font-display text-xl font-bold tracking-tight text-neutral-900">{{ pageTitle }}</h1>
                <!-- Breadcrumb placeholder could go here -->
              </div>
            </div>

            <div class="flex items-center gap-4">
              <div class="hidden text-right sm:block">
                <p class="text-sm font-semibold text-neutral-900">{{ authStore.user?.name ?? 'Usuário' }}</p>
                <p class="text-xs font-medium text-neutral-500">{{ authStore.user?.role ?? 'Sem sessão' }}</p>
              </div>
              <div class="h-8 w-px bg-neutral-200 hidden sm:block"></div>
              <Button variant="ghost" size="sm" class="text-neutral-500 hover:text-rose-600 hover:bg-rose-50 rounded-full w-9 h-9 p-0 flex items-center justify-center" @click="authStore.logout" aria-label="Sair">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
              </Button>
            </div>
          </div>
        </header>

        <!-- Page Content -->
        <main class="mx-auto max-w-7xl px-6 pb-6 pt-2">
          <div class="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <slot />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>
