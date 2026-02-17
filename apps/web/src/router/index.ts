import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { getActivePinia } from 'pinia'

import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { pinia } from '@/stores'
import type { UserRole } from '@/types/auth'

declare module 'vue-router' {
  interface RouteMeta {
    layout?: 'auth' | 'default'
    requiresAuth?: boolean
    roles?: UserRole[]
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      layout: 'auth',
    },
  },
  {
    path: '/',
    redirect: () => {
      const activePinia = getActivePinia() ?? pinia
      const authStore = useAuthStore(activePinia)
      authStore.loadFromStorage()
      if (!authStore.isAuthenticated) {
        return '/login'
      }
      return authStore.isAdmin ? '/dashboard' : '/client-dashboard'
    },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
  {
    path: '/client-dashboard',
    name: 'client-dashboard',
    component: () => import('@/views/client/ClientDashboardView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
  {
    path: '/profile',
    name: 'client-profile',
    component: () => import('@/views/client/ProfileView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
  {
    path: '/my-pets',
    name: 'client-pets',
    component: () => import('@/views/client/PetsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
  {
    path: '/my-appointments',
    name: 'client-appointments',
    component: () => import('@/views/client/AppointmentsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['CLIENTE'],
    },
  },
  {
    path: '/admin/clients',
    name: 'admin-clients',
    component: () => import('@/views/admin/ClientsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('@/views/admin/UsersView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
  {
    path: '/admin/breeds',
    name: 'admin-breeds',
    component: () => import('@/views/admin/BreedsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
  {
    path: '/admin/pets',
    name: 'admin-pets',
    component: () => import('@/views/admin/PetsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
  {
    path: '/admin/appointments',
    name: 'admin-appointments',
    component: () => import('@/views/admin/AppointmentsView.vue'),
    meta: {
      layout: 'default',
      requiresAuth: true,
      roles: ['ADMIN'],
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function getDefaultRoute(role: UserRole | null | undefined): string {
  if (role === 'ADMIN') {
    return '/dashboard'
  }
  if (role === 'CLIENTE') {
    return '/client-dashboard'
  }
  return '/login'
}

router.beforeEach((to) => {
  const activePinia = getActivePinia() ?? pinia
  const authStore = useAuthStore(activePinia)
  authStore.loadFromStorage()

  if (to.path === '/login' && authStore.isAuthenticated) {
    return getDefaultRoute(authStore.role)
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.meta.roles?.length) {
    const requestedRoles = to.meta.roles
    const canAdminAccessClientRoute = authStore.role === 'ADMIN' && requestedRoles.length === 1 && requestedRoles[0] === 'CLIENTE'
    if (!authStore.role || (!requestedRoles.includes(authStore.role) && !canAdminAccessClientRoute)) {
      const toastStore = useToastStore(activePinia)
      toastStore.push({
        title: 'Acesso negado',
        description: 'Você não tem permissão para acessar esta página.',
        variant: 'error',
      })
      return getDefaultRoute(authStore.role)
    }
  }

  return true
})

export default router
