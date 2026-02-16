import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

type UserRole = 'ADMIN' | 'CLIENTE'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const role = ref<UserRole | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function setSession(newToken: string, newRole: UserRole) {
    token.value = newToken
    role.value = newRole
  }

  function clearSession() {
    token.value = null
    role.value = null
  }

  return {
    token,
    role,
    isAuthenticated,
    setSession,
    clearSession,
  }
})
