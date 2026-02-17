from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.application.auth_use_case import AuthUseCase
from metaway_api.domain.exceptions import AuthenticationError
from metaway_api.infra.database import get_db_session
from metaway_api.interfaces.schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Realiza login com CPF (campo username) e senha, retornando token JWT.",
    responses={
        200: {"description": "Login efetuado com sucesso."},
        401: {"description": "Credenciais inválidas."},
    },
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    cpf = "".join(char for char in form_data.username if char.isdigit())
    try:
        token = await AuthUseCase(session).login(cpf, form_data.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return TokenResponse(access_token=token)
