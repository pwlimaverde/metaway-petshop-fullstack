import type { JwtPayload, UserRole } from '@/types/auth'

function decodeBase64Url(value: string): string {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/')
  const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=')
  return atob(padded)
}

export function decodeJwtPayload(token: string): JwtPayload | null {
  const parts = token.split('.')
  if (parts.length !== 3) {
    return null
  }

  const payloadSegment = parts[1]
  if (!payloadSegment) {
    return null
  }

  try {
    const payload = JSON.parse(decodeBase64Url(payloadSegment)) as Partial<JwtPayload>
    if (!payload.sub || !payload.role || typeof payload.exp !== 'number') {
      return null
    }
    return {
      sub: String(payload.sub),
      role: payload.role as UserRole,
      client_id: payload.client_id ?? null,
      exp: payload.exp,
    }
  } catch {
    return null
  }
}

export function isJwtExpired(payload: JwtPayload): boolean {
  return Date.now() >= payload.exp * 1000
}
