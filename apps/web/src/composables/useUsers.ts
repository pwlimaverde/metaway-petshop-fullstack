import { api } from '@/lib/api'
import type { UserEntity } from '@/types/entities'

export interface UserPayload {
  cpf: string
  name?: string | null
  role: 'ADMIN' | 'CLIENTE'
  password?: string
  client_id?: number | null
}

export interface PasswordChangePayload {
  current_password: string
  new_password: string
}

export function useUsers() {
  async function list(offset = 0, limit = 200) {
    const response = await api.get<UserEntity[]>('/users', { params: { offset, limit } })
    return response.data
  }

  async function create(payload: UserPayload) {
    const response = await api.post<UserEntity>('/users', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<UserPayload>) {
    const response = await api.patch<UserEntity>(`/users/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/users/${id}`)
  }

  async function changeMyPassword(payload: PasswordChangePayload) {
    await api.patch('/users/me/password', payload)
  }

  return {
    list,
    create,
    update,
    remove,
    changeMyPassword,
  }
}
