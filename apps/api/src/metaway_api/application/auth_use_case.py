from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.exceptions import AuthenticationError
from metaway_api.infra.auth import create_access_token
from metaway_api.infra.repositories import UserRepository
from metaway_api.infra.security import verify_password


class AuthUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def login(self, cpf: str, password: str) -> str:
        user = await self._users.get_by_cpf(cpf)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("CPF ou senha inválidos.")
        return create_access_token(user)
