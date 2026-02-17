export const MIN_PASSWORD_LENGTH = 6
export const MIN_PASSWORD_DIGITS = 3

export function isStrongPassword(value: string): boolean {
  if (value.length < MIN_PASSWORD_LENGTH) {
    return false
  }
  const digitsCount = (value.match(/\d/g) ?? []).length
  return digitsCount >= MIN_PASSWORD_DIGITS
}
