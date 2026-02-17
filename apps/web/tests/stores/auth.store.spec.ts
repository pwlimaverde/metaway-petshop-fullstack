import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY, api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

function createToken(role: 'ADMIN' | 'CLIENTE', clientId: number | null, expiresInSeconds = 3600): string {
  const now = Math.floor(Date.now() / 1000)
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url')
  const payload = Buffer.from(
    JSON.stringify({
      sub: '1',
      role,
      client_id: clientId,
      exp: now + expiresInSeconds,
    }),
  ).toString('base64url')
  return `${header}.${payload}.signature`
}

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('realiza login e persiste sessão', async () => {
    const token = createToken('CLIENTE', 99)

    vi.spyOn(api, 'post').mockResolvedValue({
      data: {
        access_token: token,
        token_type: 'bearer',
      },
    })

    vi.spyOn(api, 'get').mockResolvedValue({
      data: {
        id: 99,
        name: 'Cliente Teste',
        cpf: '12345678909',
        photo_url: null,
        created_at: '2025-01-01T00:00:00',
      },
    })

    const store = useAuthStore()
    await store.login('123.456.789-00', 'senha123')

    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.role).toBe('CLIENTE')
    expect(store.user?.name).toBe('Cliente Teste')
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBe(token)
    expect(localStorage.getItem(USER_STORAGE_KEY)).toContain('Cliente Teste')
  })

  it('mantém estado limpo quando login falha', async () => {
    vi.spyOn(api, 'post').mockRejectedValue(new Error('invalid credentials'))

    const store = useAuthStore()
    await expect(store.login('12345678900', 'senha-incorreta')).rejects.toThrow('invalid credentials')

    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
  })

  it('carrega sessão persistida do localStorage', () => {
    const token = createToken('ADMIN', null)
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({
        id: 1,
        cpf: '52998224725',
        name: 'Admin',
        role: 'ADMIN',
        client_id: null,
      }),
    )

    const store = useAuthStore()
    store.loadFromStorage()

    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.role).toBe('ADMIN')
    expect(store.hasLoadedFromStorage).toBe(true)
  })

  it('logout limpa sessão', () => {
    const token = createToken('ADMIN', null)
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({
        id: 1,
        cpf: '52998224725',
        name: 'Admin',
        role: 'ADMIN',
        client_id: null,
      }),
    )

    const store = useAuthStore()
    store.loadFromStorage()
    store.logout(false)

    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
  })

  it('rejeita token expirado ao carregar do storage', () => {
    const expiredToken = createToken('ADMIN', null, -60)
    localStorage.setItem(TOKEN_STORAGE_KEY, expiredToken)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 1, cpf: '52998224725', name: 'Admin', role: 'ADMIN', client_id: null }),
    )

    const store = useAuthStore()
    store.loadFromStorage()

    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull()
  })

  it('rejeita token com formato inválido', () => {
    localStorage.setItem(TOKEN_STORAGE_KEY, 'token-invalido')
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 1, cpf: '52998224725', name: 'Admin', role: 'ADMIN', client_id: null }),
    )

    const store = useAuthStore()
    store.loadFromStorage()

    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
  })

  it('getter isAdmin retorna true para ADMIN', () => {
    const token = createToken('ADMIN', null)
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 1, cpf: '52998224725', name: 'Admin', role: 'ADMIN', client_id: null }),
    )

    const store = useAuthStore()
    store.loadFromStorage()

    expect(store.isAdmin).toBe(true)
    expect(store.isCliente).toBe(false)
  })

  it('getter isCliente retorna true para CLIENTE', () => {
    const token = createToken('CLIENTE', 99)
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 99, cpf: '12345678909', name: 'Cliente', role: 'CLIENTE', client_id: 99 }),
    )

    const store = useAuthStore()
    store.loadFromStorage()

    expect(store.isCliente).toBe(true)
    expect(store.isAdmin).toBe(false)
  })

  it('não carrega do storage mais de uma vez', () => {
    const token = createToken('ADMIN', null)
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 1, cpf: '52998224725', name: 'Admin', role: 'ADMIN', client_id: null }),
    )

    const store = useAuthStore()
    store.loadFromStorage()
    expect(store.hasLoadedFromStorage).toBe(true)

    localStorage.clear()
    store.loadFromStorage()

    expect(store.isAuthenticated).toBe(true)
  })

  it('normaliza CPF removendo caracteres não numéricos antes do login', async () => {
    const token = createToken('CLIENTE', 99)
    const postSpy = vi.spyOn(api, 'post').mockResolvedValue({
      data: { access_token: token, token_type: 'bearer' },
    })
    vi.spyOn(api, 'get').mockResolvedValue({
      data: { id: 99, name: 'Cliente', cpf: '12345678909', photo_url: null, created_at: '2025-01-01' },
    })

    const store = useAuthStore()
    await store.login('123.456.789-00', 'senha123')

    expect(postSpy).toHaveBeenCalledWith(
      '/auth/login',
      expect.any(URLSearchParams),
      expect.objectContaining({ headers: expect.any(Object) }),
    )

    const sentForm = postSpy.mock.calls[0][1] as URLSearchParams
    expect(sentForm.get('username')).toBe('12345678900')
  })
})
