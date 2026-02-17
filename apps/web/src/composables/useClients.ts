import { api } from '@/lib/api'
import type { Client } from '@/types/entities'

export interface ClientPayload {
  cpf: string
  name: string
  photo_url?: string | null
}

export function useClients() {
  async function list(offset = 0, limit = 100) {
    const response = await api.get<Client[]>('/clients', { params: { offset, limit } })
    return response.data
  }

  async function getMe() {
    const response = await api.get<Client>('/clients/me')
    return response.data
  }

  async function create(payload: ClientPayload) {
    const response = await api.post<Client>('/clients', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<ClientPayload>) {
    const response = await api.patch<Client>(`/clients/${id}`, payload)
    return response.data
  }

  async function updateMe(payload: Partial<ClientPayload>) {
    const response = await api.patch<Client>('/clients/me', payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/clients/${id}`)
  }

  async function uploadPhoto(id: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<{ photo_url: string }>(`/clients/${id}/photo`, formData)
    return response.data
  }

  return {
    list,
    getMe,
    create,
    update,
    updateMe,
    remove,
    uploadPhoto,
  }
}
