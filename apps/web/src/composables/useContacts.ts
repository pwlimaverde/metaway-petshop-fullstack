import { api } from '@/lib/api'
import type { Contact } from '@/types/entities'

export interface ContactPayload {
  tag: string
  tipo: 'EMAIL' | 'TELEFONE'
  valor: string
}

export function useContacts() {
  async function listByClient(clientId: number) {
    const response = await api.get<Contact[]>(`/clients/${clientId}/contacts`)
    return response.data
  }

  async function listMine() {
    const response = await api.get<Contact[]>('/clients/me/contacts')
    return response.data
  }

  async function createForClient(clientId: number, payload: ContactPayload) {
    const response = await api.post<Contact>(`/clients/${clientId}/contacts`, payload)
    return response.data
  }

  async function createMine(payload: ContactPayload) {
    const response = await api.post<Contact>('/clients/me/contacts', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<ContactPayload>) {
    const response = await api.patch<Contact>(`/contacts/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/contacts/${id}`)
  }

  return {
    listByClient,
    listMine,
    createForClient,
    createMine,
    update,
    remove,
  }
}
