from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from metaway_api.domain.enums import AppointmentStatus, ContactType, UserRole
from metaway_api.domain.validators import validate_cpf
from metaway_api.infra.security import validate_password_strength


def _normalize_cpf(value: str) -> str:
    return validate_cpf(value)


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

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


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

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        validate_password_strength(value)
        return value


class UserResponse(BaseResponseSchema):
    id: int
    cpf: str
    name: str
    role: UserRole
    client_id: int | None
    created_at: datetime
    updated_at: datetime


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class ClientCreate(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    name: str = Field(min_length=1, max_length=255)
    photo_url: str | None = Field(default=None, max_length=512)

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str) -> str:
        return _normalize_cpf(value)


class ClientUpdate(BaseModel):
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    name: str | None = Field(default=None, min_length=1, max_length=255)
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
    updated_at: datetime


class AddressCreate(BaseModel):
    logradouro: str = Field(min_length=1, max_length=255)
    numero: str = Field(min_length=1, max_length=20)
    complemento: str | None = Field(default=None, max_length=255)
    bairro: str = Field(min_length=1, max_length=120)
    cidade: str = Field(min_length=1, max_length=120)
    estado: str = Field(min_length=2, max_length=2)
    cep: str = Field(min_length=1, max_length=10)
    tag: str = Field(min_length=1, max_length=60)


class AddressUpdate(BaseModel):
    logradouro: str | None = Field(default=None, min_length=1, max_length=255)
    numero: str | None = Field(default=None, min_length=1, max_length=20)
    complemento: str | None = Field(default=None, max_length=255)
    bairro: str | None = Field(default=None, min_length=1, max_length=120)
    cidade: str | None = Field(default=None, min_length=1, max_length=120)
    estado: str | None = Field(default=None, min_length=2, max_length=2)
    cep: str | None = Field(default=None, min_length=1, max_length=10)
    tag: str | None = Field(default=None, min_length=1, max_length=60)


class AddressResponse(BaseResponseSchema):
    id: int
    client_id: int
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    estado: str
    cep: str
    tag: str
    created_at: datetime
    updated_at: datetime


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
    created_at: datetime
    updated_at: datetime


class BreedCreate(BaseModel):
    descricao: str = Field(min_length=1, max_length=120)


class BreedUpdate(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=120)


class BreedResponse(BaseResponseSchema):
    id: int
    descricao: str
    created_at: datetime
    updated_at: datetime


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
    created_at: datetime
    updated_at: datetime


class AppointmentCreate(BaseModel):
    pet_id: int
    descricao: str = Field(min_length=1)
    valor: Decimal = Field(gt=0)
    data: datetime
    status: AppointmentStatus = AppointmentStatus.AGENDADO


class AppointmentUpdate(BaseModel):
    pet_id: int | None = None
    descricao: str | None = Field(default=None, min_length=1)
    valor: Decimal | None = Field(default=None, gt=0)
    data: datetime | None = None
    status: AppointmentStatus | None = None


class AppointmentResponse(BaseResponseSchema):
    id: int
    pet_id: int
    descricao: str
    valor: Decimal
    data: datetime
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime


class PhotoUploadResponse(BaseModel):
    photo_url: str
