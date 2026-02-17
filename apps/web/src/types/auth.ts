export type UserRole = 'ADMIN' | 'CLIENTE'

export interface AuthUser {
  id: number
  cpf: string
  name: string
  role: UserRole
  client_id: number | null
}

export interface LoginPayload {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface JwtPayload {
  sub: string
  role: UserRole
  client_id: number | null
  exp: number
}
