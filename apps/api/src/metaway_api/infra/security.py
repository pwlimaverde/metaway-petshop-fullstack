from passlib.context import CryptContext

_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
MIN_PASSWORD_LENGTH = 6
MIN_PASSWORD_DIGITS = 3


def validate_password_strength(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres.")
    digit_count = sum(char.isdigit() for char in password)
    if digit_count < MIN_PASSWORD_DIGITS:
        raise ValueError(f"Senha deve conter pelo menos {MIN_PASSWORD_DIGITS} dígitos.")


def hash_password(plain: str) -> str:
    return _PASSWORD_CONTEXT.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _PASSWORD_CONTEXT.verify(plain, hashed)
