from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from metaway_api.domain.enums import ContactType, UserRole


def _normalize_cpf(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if len(digits) != 11:
        raise ValueError("CPF deve conter 11 dígitos.")
    return digits


class BaseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str


class MetricsResponse(BaseModel):
    status: str = "ok"
    uptime_seconds: float
    memory_mb: float
    cpu_percent: float


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    name: str = Field(min_length=1, max_length=255)
    role: UserRole
    password: str = Field(min_length=6, max_length=128)
    client_id: int | None = None

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str) -> str:
        return _normalize_cpf(value)


class UserUpdate(BaseModel):
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    client_id: int | None = None

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_cpf(value)


class UserResponse(BaseResponseSchema):
    id: int
    cpf: str
    name: str
    role: UserRole
    client_id: int | None


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    photo_url: str | None = Field(default=None, max_length=512)

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_cpf(value)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    photo_url: str | None = Field(default=None, max_length=512)

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_cpf(value)


class ClientResponse(BaseResponseSchema):
    id: int
    name: str
    cpf: str | None
    photo_url: str | None
    created_at: datetime


class AddressCreate(BaseModel):
    logradouro: str = Field(min_length=1, max_length=255)
    cidade: str = Field(min_length=1, max_length=120)
    bairro: str = Field(min_length=1, max_length=120)
    complemento: str | None = Field(default=None, max_length=255)
    tag: str = Field(min_length=1, max_length=60)


class AddressUpdate(BaseModel):
    logradouro: str | None = Field(default=None, min_length=1, max_length=255)
    cidade: str | None = Field(default=None, min_length=1, max_length=120)
    bairro: str | None = Field(default=None, min_length=1, max_length=120)
    complemento: str | None = Field(default=None, max_length=255)
    tag: str | None = Field(default=None, min_length=1, max_length=60)


class AddressResponse(BaseResponseSchema):
    id: int
    client_id: int
    logradouro: str
    cidade: str
    bairro: str
    complemento: str | None
    tag: str


class ContactCreate(BaseModel):
    tag: str = Field(min_length=1, max_length=60)
    tipo: ContactType
    valor: str = Field(min_length=1, max_length=255)


class ContactUpdate(BaseModel):
    tag: str | None = Field(default=None, min_length=1, max_length=60)
    tipo: ContactType | None = None
    valor: str | None = Field(default=None, min_length=1, max_length=255)


class ContactResponse(BaseResponseSchema):
    id: int
    client_id: int
    tag: str
    tipo: ContactType
    valor: str


class BreedCreate(BaseModel):
    descricao: str = Field(min_length=1, max_length=120)


class BreedUpdate(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=120)


class BreedResponse(BaseResponseSchema):
    id: int
    descricao: str


class PetCreate(BaseModel):
    client_id: int
    breed_id: int
    name: str = Field(min_length=1, max_length=255)
    birth_date: date
    photo_url: str | None = Field(default=None, max_length=512)


class PetUpdate(BaseModel):
    client_id: int | None = None
    breed_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    birth_date: date | None = None
    photo_url: str | None = Field(default=None, max_length=512)


class PetResponse(BaseResponseSchema):
    id: int
    client_id: int
    breed_id: int
    name: str
    birth_date: date
    photo_url: str | None


class AppointmentCreate(BaseModel):
    pet_id: int
    descricao: str = Field(min_length=1)
    valor: Decimal = Field(gt=0)
    data: datetime


class AppointmentUpdate(BaseModel):
    pet_id: int | None = None
    descricao: str | None = Field(default=None, min_length=1)
    valor: Decimal | None = Field(default=None, gt=0)
    data: datetime | None = None


class AppointmentResponse(BaseResponseSchema):
    id: int
    pet_id: int
    descricao: str
    valor: Decimal
    data: datetime


class PhotoUploadResponse(BaseModel):
    photo_url: str
