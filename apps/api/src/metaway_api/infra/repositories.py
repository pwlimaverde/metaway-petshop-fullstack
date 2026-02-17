from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.infra.models import (
    Address,
    Appointment,
    Breed,
    Client,
    Contact,
    Pet,
    User,
)


class BaseRepository[ModelT]:
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: int) -> ModelT | None:
        return await self.session.get(self.model, record_id)

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelT]:
        stmt: Select[tuple[ModelT]] = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **data: object) -> ModelT:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, **data: object) -> ModelT:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_cpf(self, cpf: str) -> User | None:
        result = await self.session.execute(select(User).where(User.cpf == cpf))
        return result.scalar_one_or_none()


class ClientRepository(BaseRepository[Client]):
    model = Client


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def list_by_client_id(self, client_id: int) -> Sequence[Address]:
        result = await self.session.execute(
            select(Address).where(Address.client_id == client_id).order_by(Address.id)
        )
        return result.scalars().all()


class ContactRepository(BaseRepository[Contact]):
    model = Contact

    async def list_by_client_id(self, client_id: int) -> Sequence[Contact]:
        result = await self.session.execute(
            select(Contact).where(Contact.client_id == client_id).order_by(Contact.id)
        )
        return result.scalars().all()


class BreedRepository(BaseRepository[Breed]):
    model = Breed


class PetRepository(BaseRepository[Pet]):
    model = Pet

    async def list_by_client_id(
        self,
        client_id: int,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Pet]:
        result = await self.session.execute(
            select(Pet)
            .where(Pet.client_id == client_id)
            .order_by(Pet.id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()


class AppointmentRepository(BaseRepository[Appointment]):
    model = Appointment

    async def list_by_pet_ids(
        self,
        pet_ids: Sequence[int],
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Appointment]:
        if not pet_ids:
            return []

        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.pet_id.in_(pet_ids))
            .order_by(Appointment.id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
