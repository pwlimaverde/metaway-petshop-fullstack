import { api } from '@/lib/api'
import type { Appointment, AppointmentStatus } from '@/types/entities'

export interface AppointmentPayload {
  pet_id: number
  descricao: string
  valor: number
  data: string
  status?: AppointmentStatus
}

export function useAppointments() {
  async function list(offset = 0, limit = 200) {
    const response = await api.get<Appointment[]>('/appointments', { params: { offset, limit } })
    return response.data
  }

  async function create(payload: AppointmentPayload) {
    const response = await api.post<Appointment>('/appointments', payload)
    return response.data
  }

  async function update(id: number, payload: Partial<AppointmentPayload>) {
    const response = await api.patch<Appointment>(`/appointments/${id}`, payload)
    return response.data
  }

  async function remove(id: number) {
    await api.delete(`/appointments/${id}`)
  }

  return {
    list,
    create,
    update,
    remove,
  }
}
