import { api } from '@/lib/api'
import type { Pet } from '@/types/entities'

export interface PetPayload {
  client_id: number
  breed_id: number
  name: string
  birth_date: string
  photo_url?: string | null
}

export function usePets() {
  async function list(offset = 0, limit = 200) {
    const response = await api.get<Pet[]>('/pets', { params: { offset, limit } })
    return response.data
  }

  async function get(id: number) {
    const response = await api.get<Pet>(`/pets/${id}`)
    return response.data
  }

  async function create(payload: PetPayload) {
    const response = await api.post<Pet>('/pets', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<PetPayload>) {
    const response = await api.patch<Pet>(`/pets/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/pets/${id}`)
  }

  async function uploadPhoto(id: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<{ photo_url: string }>(`/pets/${id}/photo`, formData)
    return response.data
  }

  return {
    list,
    get,
    create,
    update,
    remove,
    uploadPhoto,
  }
}
