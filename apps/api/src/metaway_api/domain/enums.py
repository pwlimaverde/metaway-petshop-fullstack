from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"


class ContactType(StrEnum):
    EMAIL = "EMAIL"
    TELEFONE = "TELEFONE"
