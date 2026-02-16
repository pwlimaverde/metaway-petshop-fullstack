from passlib.context import CryptContext

_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _PASSWORD_CONTEXT.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _PASSWORD_CONTEXT.verify(plain, hashed)
