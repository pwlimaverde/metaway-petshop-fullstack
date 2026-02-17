from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"


class ContactType(StrEnum):
    EMAIL = "EMAIL"
    TELEFONE = "TELEFONE"


class AppointmentStatus(StrEnum):
    AGENDADO = "AGENDADO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"
