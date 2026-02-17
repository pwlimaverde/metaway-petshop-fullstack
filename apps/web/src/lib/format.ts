export function formatCpf(value: string): string {
  const digits = value.replace(/\D/g, '').slice(0, 11)
  return digits
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

export function isValidCpf(value: string): boolean {
  const digits = value.replace(/\D/g, '')
  if (digits.length !== 11) {
    return false
  }
  if (/^(\d)\1{10}$/.test(digits)) {
    return false
  }

  const numbers = digits.split('').map((char) => Number(char))
  for (const checkIndex of [9, 10]) {
    const weightStart = checkIndex + 1
    const total = numbers
      .slice(0, checkIndex)
      .reduce((sum, current, index) => sum + current * (weightStart - index), 0)
    const expected = (total * 10) % 11 % 10
    if (numbers[checkIndex] !== expected) {
      return false
    }
  }

  return true
}

export function toIsoDateTime(localDateTime: string): string {
  if (!localDateTime) {
    return ''
  }
  return new Date(localDateTime).toISOString()
}

export function toLocalDateTime(value: string): string {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const timezoneOffset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - timezoneOffset).toISOString().slice(0, 16)
}

export function formatDate(value: string): string {
  if (!value) {
    return '-'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleDateString('pt-BR')
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}
