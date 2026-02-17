export type ContactType = 'EMAIL' | 'TELEFONE'
export type AppointmentStatus = 'AGENDADO' | 'EM_ANDAMENTO' | 'CONCLUIDO' | 'CANCELADO'

export interface Client {
  id: number
  name: string
  cpf: string | null
  photo_url: string | null
  created_at: string
  updated_at: string
}

export interface Address {
  id: number
  client_id: number
  logradouro: string
  numero: string
  complemento: string | null
  bairro: string
  cidade: string
  estado: string
  cep: string
  tag: string
  created_at: string
  updated_at: string
}

export interface Contact {
  id: number
  client_id: number
  tag: string
  tipo: ContactType
  valor: string
  created_at: string
  updated_at: string
}

export interface Breed {
  id: number
  descricao: string
  created_at: string
  updated_at: string
}

export interface Pet {
  id: number
  client_id: number
  breed_id: number
  name: string
  birth_date: string
  photo_url: string | null
  created_at: string
  updated_at: string
}

export interface Appointment {
  id: number
  pet_id: number
  descricao: string
  valor: number
  data: string
  status: AppointmentStatus
  created_at: string
  updated_at: string
}

export interface UserEntity {
  id: number
  cpf: string
  name: string
  role: 'ADMIN' | 'CLIENTE'
  client_id: number | null
  created_at: string
  updated_at: string
}
