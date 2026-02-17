import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api, TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/lib/api'
import { decodeJwtPayload, isJwtExpired } from '@/lib/jwt'
import type { AuthResponse, AuthUser } from '@/types/auth'
import type { Client, UserEntity } from '@/types/entities'

function normalizeCpf(value: string): string {
  return value.replace(/\D/g, '')
}

function buildFallbackUser(token: string): AuthUser | null {
  const payload = decodeJwtPayload(token)
  if (!payload || isJwtExpired(payload)) {
    return null
  }

  return {
    id: Number(payload.sub),
    cpf: '',
    name: payload.role === 'ADMIN' ? 'Administrador' : 'Cliente',
    role: payload.role,
    client_id: payload.client_id,
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)
  const hasLoadedFromStorage = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const role = computed(() => user.value?.role ?? null)
  const isAdmin = computed(() => role.value === 'ADMIN')
  const isCliente = computed(() => role.value === 'CLIENTE')

  function persistSession() {
    if (token.value && user.value) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token.value)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user.value))
      return
    }

    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(USER_STORAGE_KEY)
  }

  function clearSession() {
    token.value = null
    user.value = null
    persistSession()
  }

  function setSession(nextToken: string, nextUser: AuthUser) {
    token.value = nextToken
    user.value = nextUser
    persistSession()
  }

  async function hydrateProfile() {
    if (!token.value || !user.value) {
      return
    }

    if (user.value.role === 'CLIENTE') {
      const response = await api.get<Client>('/clients/me')
      user.value = {
        ...user.value,
        name: response.data.name,
        cpf: response.data.cpf ?? user.value.cpf,
      }
      persistSession()
      return
    }

    const response = await api.get<UserEntity>(`/users/${user.value.id}`)
    user.value = {
      ...user.value,
      name: response.data.name,
      cpf: response.data.cpf,
    }
    persistSession()
  }

  async function login(username: string, password: string) {
    isLoading.value = true
    try {
      const form = new URLSearchParams()
      form.set('username', normalizeCpf(username))
      form.set('password', password)

      const response = await api.post<AuthResponse>('/auth/login', form, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const fallbackUser = buildFallbackUser(response.data.access_token)
      if (!fallbackUser) {
        throw new Error('Token inválido ou expirado.')
      }

      setSession(response.data.access_token, fallbackUser)
      try {
        await hydrateProfile()
      } catch {
        // Mantém o fallback quando o perfil não puder ser carregado.
      }
    } finally {
      isLoading.value = false
    }
  }

  function loadFromStorage() {
    if (hasLoadedFromStorage.value) {
      return
    }

    const persistedToken = localStorage.getItem(TOKEN_STORAGE_KEY)
    const persistedUser = localStorage.getItem(USER_STORAGE_KEY)

    if (!persistedToken) {
      clearSession()
      hasLoadedFromStorage.value = true
      return
    }

    const fallbackUser = buildFallbackUser(persistedToken)
    if (!fallbackUser) {
      clearSession()
      hasLoadedFromStorage.value = true
      return
    }

    if (persistedUser) {
      try {
        const parsedUser = JSON.parse(persistedUser) as AuthUser
        setSession(persistedToken, parsedUser)
        hasLoadedFromStorage.value = true
        return
      } catch {
        // Ignora estado inválido e usa fallback.
      }
    }

    setSession(persistedToken, fallbackUser)
    hasLoadedFromStorage.value = true
  }

  function logout(shouldRedirect = true) {
    clearSession()
    if (shouldRedirect) {
      window.location.assign('/login')
    }
  }

  return {
    token,
    user,
    role,
    isLoading,
    isAuthenticated,
    isAdmin,
    isCliente,
    hasLoadedFromStorage,
    login,
    logout,
    loadFromStorage,
    hydrateProfile,
  }
})
