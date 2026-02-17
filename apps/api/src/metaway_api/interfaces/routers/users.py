from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import Client, User
from metaway_api.infra.repositories import UserRepository
from metaway_api.infra.security import hash_password, verify_password
from metaway_api.interfaces.schemas import (
    PasswordChangeRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


def _validate_user_payload(
    *,
    role: UserRole | str,
    client_id: int | None,
) -> None:
    normalized_role = role.value if isinstance(role, UserRole) else role

    if normalized_role == UserRole.CLIENTE.value and client_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Usuário CLIENTE deve possuir client_id.",
        )
    if normalized_role == UserRole.ADMIN.value and client_id is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Usuário ADMIN não pode possuir client_id.",
        )


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        cpf=user.cpf,
        name=user.name or user.cpf,
        role=user.role,
        client_id=user.client_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _map_user_integrity_error(exc: IntegrityError) -> str:
    message = str(getattr(exc, "orig", exc))
    if "users_cpf_key" in message or "uq_users_cpf" in message:
        return "CPF já cadastrado."
    if "users_client_id_key" in message:
        return (
            "Este banco ainda limita 1 usuário por cliente. "
            "Execute `make migrate` para liberar múltiplos usuários "
            "vinculados ao mesmo cliente."
        )
    return "Não foi possível salvar o usuário por conflito de dados."


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description=(
        "Cria um usuário com perfil ADMIN ou CLIENTE. Acesso apenas para admin."
    ),
)
async def create_user(
    payload: UserCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    _validate_user_payload(
        role=payload.role,
        client_id=payload.client_id,
    )
    if (
        payload.client_id is not None
        and await session.get(Client, payload.client_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )

    repository = UserRepository(session)
    persisted_name = payload.name.strip() if payload.name else None

    try:
        user = await repository.create(
            cpf=payload.cpf,
            name=persisted_name,
            role=payload.role,
            password_hash=hash_password(payload.password),
            client_id=payload.client_id,
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_map_user_integrity_error(exc),
        ) from exc

    return _to_user_response(user)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuários",
    description="Lista usuários com paginação simples.",
)
async def list_users(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> list[UserResponse]:
    users = await UserRepository(session).list(offset=offset, limit=limit)
    return [_to_user_response(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Detalhar usuário",
    description="Retorna os dados de um usuário pelo ID.",
)
async def get_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    return _to_user_response(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário",
    description="Atualiza parcialmente um usuário existente.",
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )

    next_role = payload.role if payload.role is not None else user.role
    client_id_was_sent = "client_id" in payload.model_fields_set
    next_client_id = payload.client_id if client_id_was_sent else user.client_id
    _validate_user_payload(role=next_role, client_id=next_client_id)
    if (
        payload.client_id is not None
        and client_id_was_sent
        and await session.get(Client, payload.client_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )

    update_data = payload.model_dump(exclude_unset=True, exclude={"password"})
    if "name" in update_data and update_data["name"] is not None:
        update_data["name"] = update_data["name"].strip()

    if payload.password is not None:
        update_data["password_hash"] = hash_password(payload.password)

    try:
        updated = await repository.update(user, **update_data)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_map_user_integrity_error(exc),
        ) from exc

    return _to_user_response(updated)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir usuário",
    description="Exclui um usuário existente.",
)
async def delete_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado."
        )
    await repository.delete(user)
    await session.commit()


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Alterar minha senha",
    description="Permite ao usuário autenticado alterar a própria senha.",
)
async def change_my_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual inválida.",
        )

    current_user.password_hash = hash_password(payload.new_password)
    await session.commit()
