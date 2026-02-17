from sqlalchemy import select

from metaway_api.domain.enums import UserRole
from metaway_api.infra.models import Breed, User
from metaway_api.infra.repositories import AppointmentRepository, UserRepository
from metaway_api.infra.seed import DEFAULT_BREEDS, seed_initial_data
from metaway_api.infra.seed_cli import main as seed_cli_main
from metaway_api.settings import get_settings


async def test_seed_creates_admin_and_breeds(session_factory) -> None:
    settings = get_settings()

    async with session_factory() as session:
        await seed_initial_data(session)

    async with session_factory() as session:
        user = await UserRepository(session).get_by_cpf(settings.admin_seed_cpf)
        assert user is not None
        assert user.role == UserRole.ADMIN
        breeds = (await session.execute(select(Breed))).scalars().all()
        assert len(breeds) == len(DEFAULT_BREEDS)


async def test_seed_is_idempotent(session_factory) -> None:
    async with session_factory() as session:
        await seed_initial_data(session)
    async with session_factory() as session:
        await seed_initial_data(session)
    async with session_factory() as session:
        users = (
            (await session.execute(select(User).where(User.role == UserRole.ADMIN)))
            .scalars()
            .all()
        )
        assert len(users) == 1


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
