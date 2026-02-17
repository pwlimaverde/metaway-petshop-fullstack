from sqlalchemy import func, select

from metaway_api.domain.enums import UserRole
from metaway_api.infra.models import (
    Address,
    Appointment,
    Breed,
    Client,
    Contact,
    Pet,
    User,
)
from metaway_api.infra.repositories import AppointmentRepository, UserRepository
from metaway_api.infra.seed import DEFAULT_BREEDS, EXTRA_DEMO_CLIENTS, seed_initial_data
from metaway_api.infra.seed_cli import main as seed_cli_main
from metaway_api.settings import get_settings


async def _snapshot_counts(session) -> dict[str, int]:
    models = {
        "users": User,
        "clients": Client,
        "addresses": Address,
        "contacts": Contact,
        "pets": Pet,
        "appointments": Appointment,
        "breeds": Breed,
    }
    return {
        key: int((await session.execute(select(func.count(model.id)))).scalar_one())
        for key, model in models.items()
    }


async def test_seed_creates_admin_demo_client_and_breeds(session_factory) -> None:
    settings = get_settings()

    async with session_factory() as session:
        await seed_initial_data(session)

    async with session_factory() as session:
        admin_user = await UserRepository(session).get_by_cpf(settings.admin_seed_cpf)
        assert admin_user is not None
        assert admin_user.role == UserRole.ADMIN

        demo_user = await UserRepository(session).get_by_cpf(settings.demo_client_cpf)
        assert demo_user is not None
        assert demo_user.role == UserRole.CLIENTE
        assert demo_user.client_id is not None

        demo_client = await session.get(Client, demo_user.client_id)
        assert demo_client is not None
        assert demo_client.cpf == settings.demo_client_cpf

        breeds = (await session.execute(select(Breed))).scalars().all()
        assert len(breeds) == len(DEFAULT_BREEDS)

        addresses = (
            (
                await session.execute(
                    select(Address).where(Address.client_id == demo_client.id)
                )
            )
            .scalars()
            .all()
        )
        assert len(addresses) >= 2

        contacts = (
            (
                await session.execute(
                    select(Contact).where(Contact.client_id == demo_client.id)
                )
            )
            .scalars()
            .all()
        )
        assert len(contacts) >= 2

        pets = (
            (await session.execute(select(Pet).where(Pet.client_id == demo_client.id)))
            .scalars()
            .all()
        )
        assert len(pets) >= 3
        assert len({pet.breed_id for pet in pets}) >= 3

        pet_ids = [pet.id for pet in pets]
        appointments = (
            (
                await session.execute(
                    select(Appointment).where(Appointment.pet_id.in_(pet_ids))
                )
            )
            .scalars()
            .all()
        )
        assert len(appointments) >= 5

        extra_cpfs = {client["cpf"] for client in EXTRA_DEMO_CLIENTS}
        existing_extra_cpfs = set(
            (
                await session.execute(
                    select(Client.cpf).where(Client.cpf.in_(extra_cpfs))
                )
            )
            .scalars()
            .all()
        )
        assert existing_extra_cpfs == extra_cpfs


async def test_seed_is_idempotent(session_factory) -> None:
    async with session_factory() as session:
        await seed_initial_data(session)
    async with session_factory() as session:
        first_snapshot = await _snapshot_counts(session)
    async with session_factory() as session:
        await seed_initial_data(session)
    async with session_factory() as session:
        second_snapshot = await _snapshot_counts(session)

    assert second_snapshot == first_snapshot


async def test_seed_only_if_empty_mode_skips_existing_database(session_factory) -> None:
    settings = get_settings()
    existing_client_cpf = "27182818205"
    async with session_factory() as session:
        session.add(Client(name="Cliente existente", cpf=existing_client_cpf))
        await session.commit()

    async with session_factory() as session:
        await seed_initial_data(session, only_if_empty=True)

    async with session_factory() as session:
        admin_user = await UserRepository(session).get_by_cpf(settings.admin_seed_cpf)
        assert admin_user is None
        assert (
            int((await session.execute(select(func.count(Breed.id)))).scalar_one()) == 0
        )
        assert (
            int((await session.execute(select(func.count(Client.id)))).scalar_one())
            == 1
        )


async def test_repository_helpers(session_factory) -> None:
    async with session_factory() as session:
        appointment_repo = AppointmentRepository(session)
        assert await appointment_repo.list_by_pet_ids([]) == []


def test_seed_cli_main(monkeypatch) -> None:
    called = {}

    def fake_asyncio_run(coro):
        called["ok"] = True
        coro.close()

    monkeypatch.setattr("metaway_api.infra.seed_cli.asyncio.run", fake_asyncio_run)
    seed_cli_main()
    assert called["ok"] is True
