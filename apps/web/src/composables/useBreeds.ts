import { api } from '@/lib/api'
import type { Breed } from '@/types/entities'

export interface BreedPayload {
  descricao: string
}

export function useBreeds() {
  async function list(offset = 0, limit = 200) {
    const response = await api.get<Breed[]>('/breeds', { params: { offset, limit } })
    return response.data
  }

  async function create(payload: BreedPayload) {
    const response = await api.post<Breed>('/breeds', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<BreedPayload>) {
    const response = await api.patch<Breed>(`/breeds/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/breeds/${id}`)
  }

  return {
    list,
    create,
    update,
    remove,
  }
}
