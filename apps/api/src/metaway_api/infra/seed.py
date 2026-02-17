from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import AppointmentStatus, ContactType, UserRole
from metaway_api.domain.validators import validate_cpf
from metaway_api.infra.models import (
    Address,
    Appointment,
    Breed,
    Client,
    Contact,
    Pet,
    User,
)
from metaway_api.infra.security import hash_password, validate_password_strength
from metaway_api.settings import get_settings

DEFAULT_BREEDS = [
    "Labrador",
    "Golden Retriever",
    "Poodle",
    "Bulldog",
    "Shih Tzu",
    "Pastor Alemão",
    "Pinscher",
    "Vira-lata",
    "Buldogue Francês",
    "Siamês",
    "Persa",
    "Maine Coon",
]

DEMO_CLIENT_ADDRESSES = [
    {
        "tag": "Casa",
        "logradouro": "Rua das Acácias",
        "numero": "245",
        "complemento": "Apto 34",
        "bairro": "Jardim Primavera",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "04567000",
    },
    {
        "tag": "Trabalho",
        "logradouro": "Avenida Paulista",
        "numero": "1578",
        "complemento": "Conjunto 901",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01310200",
    },
]

DEMO_CLIENT_CONTACTS = [
    {"tag": "Email", "tipo": ContactType.EMAIL, "valor": "cliente.demo@metaway.pet"},
    {"tag": "Telefone", "tipo": ContactType.TELEFONE, "valor": "+5511999887766"},
]

DEMO_CLIENT_PETS = [
    {"name": "Thor", "breed": "Labrador", "birth_date": date(2020, 4, 13)},
    {"name": "Mel", "breed": "Shih Tzu", "birth_date": date(2021, 9, 28)},
    {"name": "Nina", "breed": "Persa", "birth_date": date(2019, 1, 7)},
]

DEMO_CLIENT_APPOINTMENTS = [
    {
        "pet_name": "Thor",
        "descricao": "Consulta clínica anual",
        "valor": Decimal("180.00"),
        "data": datetime(2026, 1, 15, 9, 0, tzinfo=UTC),
        "status": AppointmentStatus.CONCLUIDO,
    },
    {
        "pet_name": "Thor",
        "descricao": "Banho e tosa premium",
        "valor": Decimal("130.00"),
        "data": datetime(2026, 1, 28, 14, 30, tzinfo=UTC),
        "status": AppointmentStatus.CONCLUIDO,
    },
    {
        "pet_name": "Mel",
        "descricao": "Vacinação múltipla",
        "valor": Decimal("240.00"),
        "data": datetime(2026, 2, 2, 10, 45, tzinfo=UTC),
        "status": AppointmentStatus.EM_ANDAMENTO,
    },
    {
        "pet_name": "Nina",
        "descricao": "Avaliação dermatológica",
        "valor": Decimal("210.00"),
        "data": datetime(2026, 2, 9, 16, 15, tzinfo=UTC),
        "status": AppointmentStatus.AGENDADO,
    },
    {
        "pet_name": "Nina",
        "descricao": "Retorno pós-tratamento",
        "valor": Decimal("120.00"),
        "data": datetime(2026, 2, 20, 11, 0, tzinfo=UTC),
        "status": AppointmentStatus.AGENDADO,
    },
]

EXTRA_DEMO_CLIENTS = [
    {"name": "Fernanda Lopes", "cpf": "39053344705"},
    {"name": "Rafael Menezes", "cpf": "11144477735"},
    {"name": "Bianca Matos", "cpf": "22233366638"},
    {"name": "Carlos Teixeira", "cpf": "31415926590"},
]


def _sync_instance(instance: object, data: dict[str, object]) -> bool:
    changed = False
    for field, value in data.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
            changed = True
    return changed


async def _is_database_empty(session: AsyncSession) -> bool:
    for model in (User, Client, Breed):
        result = await session.execute(select(model.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return False
    return True


async def _ensure_demo_client_data(
    session: AsyncSession, demo_client: Client, breeds_by_name: dict[str, Breed]
) -> bool:
    has_changes = False

    addresses_rows = await session.execute(
        select(Address).where(Address.client_id == demo_client.id)
    )
    addresses_by_tag = {
        address.tag.lower(): address for address in addresses_rows.scalars().all()
    }
    for payload in DEMO_CLIENT_ADDRESSES:
        key = payload["tag"].lower()
        existing = addresses_by_tag.get(key)
        if existing is None:
            session.add(Address(client_id=demo_client.id, **payload))
            has_changes = True
            continue
        if _sync_instance(existing, payload):
            has_changes = True

    contacts_rows = await session.execute(
        select(Contact).where(Contact.client_id == demo_client.id)
    )
    contacts_by_tag = {
        contact.tag.lower(): contact for contact in contacts_rows.scalars().all()
    }
    for payload in DEMO_CLIENT_CONTACTS:
        key = payload["tag"].lower()
        existing = contacts_by_tag.get(key)
        if existing is None:
            session.add(Contact(client_id=demo_client.id, **payload))
            has_changes = True
            continue
        if _sync_instance(existing, payload):
            has_changes = True

    pets_rows = await session.execute(
        select(Pet).where(Pet.client_id == demo_client.id)
    )
    pets_by_name = {pet.name.lower(): pet for pet in pets_rows.scalars().all()}
    for payload in DEMO_CLIENT_PETS:
        pet_data = {
            "breed_id": breeds_by_name[payload["breed"]].id,
            "name": payload["name"],
            "birth_date": payload["birth_date"],
        }
        key = payload["name"].lower()
        existing = pets_by_name.get(key)
        if existing is None:
            session.add(Pet(client_id=demo_client.id, **pet_data))
            has_changes = True
            continue
        if _sync_instance(existing, pet_data):
            has_changes = True

    if has_changes:
        await session.flush()

    pets_rows = await session.execute(
        select(Pet).where(Pet.client_id == demo_client.id)
    )
    pets_by_name = {pet.name.lower(): pet for pet in pets_rows.scalars().all()}
    pet_ids = [pet.id for pet in pets_by_name.values()]
    appointments_by_key: dict[tuple[int, str], Appointment] = {}
    if pet_ids:
        appointments_rows = await session.execute(
            select(Appointment).where(Appointment.pet_id.in_(pet_ids))
        )
        appointments_by_key = {
            (appointment.pet_id, appointment.descricao): appointment
            for appointment in appointments_rows.scalars().all()
        }

    for payload in DEMO_CLIENT_APPOINTMENTS:
        pet = pets_by_name[payload["pet_name"].lower()]
        key = (pet.id, payload["descricao"])
        appointment_data = {
            "descricao": payload["descricao"],
            "valor": payload["valor"],
            "data": payload["data"],
            "status": payload["status"],
        }
        existing = appointments_by_key.get(key)
        if existing is None:
            session.add(Appointment(pet_id=pet.id, **appointment_data))
            has_changes = True
            continue
        if _sync_instance(existing, appointment_data):
            has_changes = True

    return has_changes


async def seed_initial_data(
    session: AsyncSession, *, only_if_empty: bool = False
) -> None:
    settings = get_settings()
    admin_seed_cpf = validate_cpf(settings.admin_seed_cpf)
    demo_client_cpf = validate_cpf(settings.demo_client_cpf)
    validate_password_strength(settings.admin_seed_password)
    validate_password_strength(settings.demo_client_password)

    if only_if_empty and not await _is_database_empty(session):
        return

    has_changes = False

    result = await session.execute(select(User).where(User.cpf == admin_seed_cpf))
    admin_user = result.scalar_one_or_none()
    if admin_user is None:
        session.add(
            User(
                cpf=admin_seed_cpf,
                name=settings.admin_seed_name,
                role=UserRole.ADMIN,
                password_hash=hash_password(settings.admin_seed_password),
            )
        )
        has_changes = True

    existing_breeds_rows = await session.execute(select(Breed))
    existing_breeds = {
        breed.descricao: breed for breed in existing_breeds_rows.scalars().all()
    }
    for breed in DEFAULT_BREEDS:
        if breed not in existing_breeds:
            model = Breed(descricao=breed)
            session.add(model)
            existing_breeds[breed] = model
            has_changes = True

    if has_changes:
        await session.flush()

    demo_client_row = await session.execute(
        select(Client).where(Client.cpf == demo_client_cpf)
    )
    demo_client = demo_client_row.scalar_one_or_none()
    if demo_client is None:
        demo_client = Client(name=settings.demo_client_name, cpf=demo_client_cpf)
        session.add(demo_client)
        has_changes = True
    elif _sync_instance(
        demo_client, {"name": settings.demo_client_name, "cpf": demo_client_cpf}
    ):
        has_changes = True

    if demo_client.id is None:
        await session.flush()

    demo_user_row = await session.execute(
        select(User).where(User.cpf == demo_client_cpf)
    )
    demo_user = demo_user_row.scalar_one_or_none()
    if demo_user is None:
        session.add(
            User(
                cpf=demo_client_cpf,
                role=UserRole.CLIENTE,
                password_hash=hash_password(settings.demo_client_password),
                client_id=demo_client.id,
            )
        )
        has_changes = True
    elif _sync_instance(
        demo_user,
        {
            "name": None,
            "role": UserRole.CLIENTE,
            "client_id": demo_client.id,
        },
    ):
        has_changes = True

    if await _ensure_demo_client_data(session, demo_client, existing_breeds):
        has_changes = True

    existing_clients_rows = await session.execute(select(Client))
    clients_by_cpf = {
        client.cpf: client
        for client in existing_clients_rows.scalars().all()
        if client.cpf
    }
    for extra_client in EXTRA_DEMO_CLIENTS:
        cpf = validate_cpf(extra_client["cpf"])
        existing = clients_by_cpf.get(cpf)
        if existing is None:
            session.add(Client(name=extra_client["name"], cpf=cpf))
            has_changes = True
            continue
        if _sync_instance(existing, {"name": extra_client["name"], "cpf": cpf}):
            has_changes = True

    if has_changes:
        await session.commit()
