import pytest

from metaway_api.application.auth_use_case import AuthUseCase
from metaway_api.domain.enums import UserRole
from metaway_api.domain.exceptions import AuthenticationError
from metaway_api.infra.models import User
from metaway_api.infra.security import hash_password


async def test_login_success(session_factory) -> None:
    async with session_factory() as session:
        user = User(
            cpf="92832764851",
            name="Test User",
            role=UserRole.ADMIN,
            password_hash=hash_password("TestPass1!"),
        )
        session.add(user)
        await session.commit()

    async with session_factory() as session:
        use_case = AuthUseCase(session)
        token = await use_case.login("92832764851", "TestPass1!")
        assert isinstance(token, str)
        assert len(token) > 0


async def test_login_wrong_password(session_factory) -> None:
    async with session_factory() as session:
        user = User(
            cpf="35030564160",
            name="Test User 2",
            role=UserRole.ADMIN,
            password_hash=hash_password("CorrectPass1!"),
        )
        session.add(user)
        await session.commit()

    async with session_factory() as session:
        use_case = AuthUseCase(session)
        with pytest.raises(AuthenticationError):
            await use_case.login("35030564160", "WrongPass1!")


async def test_login_unknown_cpf(session_factory) -> None:
    async with session_factory() as session:
        use_case = AuthUseCase(session)
        with pytest.raises(AuthenticationError):
            await use_case.login("39537672409", "AnyPass1!")
