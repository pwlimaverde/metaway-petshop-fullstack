from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from metaway_api.domain.enums import AppointmentStatus, ContactType, UserRole


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_cpf", "cpf"),
        CheckConstraint(
            "(role <> 'CLIENTE') OR (client_id IS NOT NULL)",
            name="ck_users_cliente_requires_client",
        ),
        CheckConstraint(
            "(role <> 'ADMIN') OR (client_id IS NULL)",
            name="ck_users_admin_without_client",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.CLIENTE,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    client: Mapped[Client | None] = relationship(
        "Client",
        back_populates="users",
        lazy="joined",
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True, unique=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="client",
        lazy="selectin",
    )
    addresses: Mapped[list[Address]] = relationship(
        "Address",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    contacts: Mapped[list[Contact]] = relationship(
        "Contact",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    pets: Mapped[list[Pet]] = relationship(
        "Pet",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = (Index("ix_addresses_client_id", "client_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    logradouro: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bairro: Mapped[str] = mapped_column(String(120), nullable=False)
    cidade: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(10), nullable=False)
    tag: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    client: Mapped[Client] = relationship(
        "Client", back_populates="addresses", lazy="joined"
    )


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (Index("ix_contacts_client_id", "client_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(60), nullable=False)
    tipo: Mapped[ContactType] = mapped_column(
        SQLEnum(ContactType, name="contact_type", native_enum=False),
        nullable=False,
    )
    valor: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    client: Mapped[Client] = relationship(
        "Client", back_populates="contacts", lazy="joined"
    )


class Breed(Base):
    __tablename__ = "breeds"
    __table_args__ = (Index("ix_breeds_descricao", "descricao"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descricao: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    pets: Mapped[list[Pet]] = relationship(
        "Pet", back_populates="breed", lazy="selectin"
    )


class Pet(Base):
    __tablename__ = "pets"
    __table_args__ = (
        Index("ix_pets_client_id", "client_id"),
        Index("ix_pets_breed_id", "breed_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    breed_id: Mapped[int] = mapped_column(
        ForeignKey("breeds.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    client: Mapped[Client] = relationship(
        "Client", back_populates="pets", lazy="joined"
    )
    breed: Mapped[Breed] = relationship("Breed", back_populates="pets", lazy="joined")
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="pet",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_pet_id", "pet_id"),
        Index("ix_appointments_data", "data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="CASCADE"),
        nullable=False,
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus, name="appointment_status", native_enum=False),
        nullable=False,
        default=AppointmentStatus.AGENDADO,
        server_default="AGENDADO",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    pet: Mapped[Pet] = relationship("Pet", back_populates="appointments", lazy="joined")
