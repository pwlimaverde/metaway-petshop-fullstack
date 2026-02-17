import { beforeEach, describe, expect, it } from 'vitest'

import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/lib/api'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { pinia } from '@/stores'

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

function persistSession(role: 'ADMIN' | 'CLIENTE', clientId: number | null) {
  const token = createToken(role, clientId)
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
  localStorage.setItem(
    USER_STORAGE_KEY,
    JSON.stringify({
      id: 1,
      cpf: role === 'ADMIN' ? '52998224725' : '12345678909',
      name: role === 'ADMIN' ? 'Admin' : 'Cliente',
      role,
      client_id: clientId,
    }),
  )

  const store = useAuthStore(pinia)
  store.hasLoadedFromStorage = false
}

describe('router guards', () => {
  beforeEach(async () => {
    localStorage.clear()

    const store = useAuthStore(pinia)
    store.token = null
    store.user = null
    store.hasLoadedFromStorage = false

    await router.push('/login')
  })

  it('redireciona para login quando acessa rota protegida sem token', async () => {
    await router.push('/dashboard')

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redireciona cliente ao tentar acessar rota de admin', async () => {
    persistSession('CLIENTE', 15)

    await router.push('/admin/clients')

    expect(router.currentRoute.value.path).toBe('/client-dashboard')
  })

  it('permite admin em rota de cliente', async () => {
    persistSession('ADMIN', null)

    await router.push('/my-pets')

    expect(router.currentRoute.value.path).toBe('/my-pets')
  })

  it('mantém rota de login pública', async () => {
    await router.push('/login')

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redireciona autenticado de /login para /dashboard', async () => {
    persistSession('ADMIN', null)

    // Navigate to /dashboard first so loadFromStorage hydrates the session
    await router.push('/dashboard')
    // Now try /login — guard should redirect back to /dashboard
    await router.push('/login')

    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('permite admin acessar rota admin', async () => {
    persistSession('ADMIN', null)

    await router.push('/admin/clients')

    expect(router.currentRoute.value.path).toBe('/admin/clients')
  })

  it('permite cliente acessar suas próprias rotas', async () => {
    persistSession('CLIENTE', 15)

    await router.push('/profile')
    expect(router.currentRoute.value.path).toBe('/profile')

    await router.push('/my-pets')
    expect(router.currentRoute.value.path).toBe('/my-pets')
  })

  it('redireciona cliente bloqueado de todas as rotas admin', async () => {
    persistSession('CLIENTE', 15)

    const adminPaths = ['/admin/clients', '/admin/users', '/admin/breeds', '/admin/pets', '/admin/appointments']

    for (const path of adminPaths) {
      await router.push('/login')
      const store = useAuthStore(pinia)
      store.hasLoadedFromStorage = false
      persistSession('CLIENTE', 15)

      await router.push(path)
      expect(router.currentRoute.value.path).toBe('/client-dashboard')
    }
  })

  it('redireciona para login com redirect query quando não autenticado', async () => {
    await router.push('/my-pets')

    expect(router.currentRoute.value.path).toBe('/login')
    expect(router.currentRoute.value.query.redirect).toBe('/my-pets')
  })

  it('redireciona para login com token expirado', async () => {
    const expiredToken = createToken('ADMIN', null, -60)
    localStorage.setItem(TOKEN_STORAGE_KEY, expiredToken)
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ id: 1, cpf: '52998224725', name: 'Admin', role: 'ADMIN', client_id: null }),
    )

    const store = useAuthStore(pinia)
    store.hasLoadedFromStorage = false

    await router.push('/dashboard')

    expect(router.currentRoute.value.path).toBe('/login')
  })
})
