from __future__ import annotations

import os

os.environ.setdefault("POSTGRES_PASSWORD", "test_only")
os.environ.setdefault("JWT_SECRET_KEY", "test_only_secret_key_with_32bytes!")
os.environ.setdefault("ADMIN_SEED_PASSWORD", "Test123")
os.environ.setdefault("DEMO_CLIENT_PASSWORD", "Client123!")

from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TypedDict

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from metaway_api.domain.enums import ContactType, UserRole
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import (
    Address,
    Appointment,
    Base,
    Breed,
    Client,
    Contact,
    Pet,
    User,
)
from metaway_api.infra.security import hash_password
from metaway_api.interfaces.routers.auth import limiter as auth_limiter
from metaway_api.main import app
from metaway_api.settings import get_settings


class SeedData(TypedDict):
    admin_user_id: int
    admin_cpf: str
    admin_password: str
    client_user_id: int
    client_cpf: str
    client_password: str
    other_client_user_id: int
    other_client_cpf: str
    other_client_password: str
    client_id: int
    other_client_id: int
    breed_id: int
    other_breed_id: int
    pet_id: int
    other_pet_id: int
    appointment_id: int
    other_appointment_id: int
    address_id: int
    other_address_id: int
    contact_id: int
    other_contact_id: int


@pytest_asyncio.fixture
async def session_factory(
    tmp_path: Path,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    settings = get_settings()
    old_upload_dir = settings.upload_dir
    old_seed_behavior = settings.run_seed_on_startup
    settings.upload_dir = str(tmp_path / "storage")
    settings.run_seed_on_startup = False

    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    yield session_maker

    app.dependency_overrides.clear()
    settings.upload_dir = old_upload_dir
    settings.run_seed_on_startup = old_seed_behavior
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def reset_auth_rate_limiter() -> AsyncIterator[None]:
    storage = getattr(auth_limiter, "_storage", None)
    if storage is not None and hasattr(storage, "reset"):
        storage.reset()
    yield
    if storage is not None and hasattr(storage, "reset"):
        storage.reset()


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def seed_data(session_factory: async_sessionmaker[AsyncSession]) -> SeedData:
    admin_password = "Admin123!"
    client_password = "Client123!"
    other_client_password = "Other123!"

    async with session_factory() as session:
        client = Client(name="Cliente Principal", cpf="12345678909")
        other_client = Client(name="Cliente Secundário", cpf="39053344705")
        breed = Breed(descricao="Labrador")
        other_breed = Breed(descricao="Poodle")
        session.add_all([client, other_client, breed, other_breed])
        await session.flush()

        admin_user = User(
            cpf="52998224725",
            name="Administrador",
            role=UserRole.ADMIN,
            password_hash=hash_password(admin_password),
        )
        client_user = User(
            cpf="12345678909",
            name="Cliente Principal",
            role=UserRole.CLIENTE,
            password_hash=hash_password(client_password),
            client_id=client.id,
        )
        other_client_user = User(
            cpf="39053344705",
            name="Cliente Secundário",
            role=UserRole.CLIENTE,
            password_hash=hash_password(other_client_password),
            client_id=other_client.id,
        )
        session.add_all([admin_user, client_user, other_client_user])
        await session.flush()

        address = Address(
            client_id=client.id,
            logradouro="Rua 1",
            numero="100",
            complemento="Apto 1",
            bairro="Centro",
            cidade="São Paulo",
            estado="SP",
            cep="01001000",
            tag="casa",
        )
        other_address = Address(
            client_id=other_client.id,
            logradouro="Rua 2",
            numero="200",
            complemento=None,
            bairro="Zona Sul",
            cidade="Rio de Janeiro",
            estado="RJ",
            cep="20040020",
            tag="trabalho",
        )
        contact = Contact(
            client_id=client.id,
            tag="principal",
            tipo=ContactType.EMAIL,
            valor="cliente@example.com",
        )
        other_contact = Contact(
            client_id=other_client.id,
            tag="principal",
            tipo=ContactType.TELEFONE,
            valor="+5511999999999",
        )
        session.add_all([address, other_address, contact, other_contact])
        await session.flush()

        pet = Pet(
            client_id=client.id,
            breed_id=breed.id,
            name="Rex",
            birth_date=date(2020, 1, 1),
        )
        other_pet = Pet(
            client_id=other_client.id,
            breed_id=other_breed.id,
            name="Bolt",
            birth_date=date(2021, 2, 2),
        )
        session.add_all([pet, other_pet])
        await session.flush()

        appointment = Appointment(
            pet_id=pet.id,
            descricao="Banho e tosa",
            valor=Decimal("99.90"),
            data=datetime.now(UTC),
        )
        other_appointment = Appointment(
            pet_id=other_pet.id,
            descricao="Consulta",
            valor=Decimal("120.00"),
            data=datetime.now(UTC),
        )
        session.add_all([appointment, other_appointment])
        await session.commit()

        return {
            "admin_user_id": admin_user.id,
            "admin_cpf": admin_user.cpf,
            "admin_password": admin_password,
            "client_user_id": client_user.id,
            "client_cpf": client_user.cpf,
            "client_password": client_password,
            "other_client_user_id": other_client_user.id,
            "other_client_cpf": other_client_user.cpf,
            "other_client_password": other_client_password,
            "client_id": client.id,
            "other_client_id": other_client.id,
            "breed_id": breed.id,
            "other_breed_id": other_breed.id,
            "pet_id": pet.id,
            "other_pet_id": other_pet.id,
            "appointment_id": appointment.id,
            "other_appointment_id": other_appointment.id,
            "address_id": address.id,
            "other_address_id": other_address.id,
            "contact_id": contact.id,
            "other_contact_id": other_contact.id,
        }


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient,
) -> Callable[[str, str], Awaitable[dict[str, str]]]:
    async def _build(cpf: str, password: str) -> dict[str, str]:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": cpf, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _build
