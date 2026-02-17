import { api } from '@/lib/api'
import type { Address } from '@/types/entities'

export interface AddressPayload {
  logradouro: string
  numero: string
  complemento?: string | null
  bairro: string
  cidade: string
  estado: string
  cep: string
  tag: string
}

export function useAddresses() {
  async function listByClient(clientId: number) {
    const response = await api.get<Address[]>(`/clients/${clientId}/addresses`)
    return response.data
  }

  async function listMine() {
    const response = await api.get<Address[]>('/clients/me/addresses')
    return response.data
  }

  async function createForClient(clientId: number, payload: AddressPayload) {
    const response = await api.post<Address>(`/clients/${clientId}/addresses`, payload)
    return response.data
  }

  async function createMine(payload: AddressPayload) {
    const response = await api.post<Address>('/clients/me/addresses', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<AddressPayload>) {
    const response = await api.patch<Address>(`/addresses/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/addresses/${id}`)
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
