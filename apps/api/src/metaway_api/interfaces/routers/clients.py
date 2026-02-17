from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import check_ownership, is_admin, require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.file_storage import save_image_upload
from metaway_api.infra.models import Client, User
from metaway_api.infra.repositories import ClientRepository
from metaway_api.interfaces.schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    PhotoUploadResponse,
)

router = APIRouter(prefix="/clients", tags=["Clients"])


async def _get_client_or_404(session: AsyncSession, client_id: int) -> Client:
    client = await ClientRepository(session).get_by_id(client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )
    return client


def _to_client_response(
    client: Client,
    *,
    cpf_override: str | None = None,
) -> ClientResponse:
    return ClientResponse(
        id=client.id,
        name=client.name,
        cpf=cpf_override if cpf_override is not None else client.cpf,
        photo_url=client.photo_url,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cliente",
    description="Cria um cliente. Acesso apenas para administradores.",
)
async def create_client(
    payload: ClientCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> ClientResponse:
    try:
        client = await ClientRepository(session).create(**payload.model_dump())
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF de cliente já cadastrado.",
        ) from exc
    return _to_client_response(client)


@router.get(
    "",
    response_model=list[ClientResponse],
    summary="Listar clientes",
    description="Lista clientes com paginação simples. Acesso admin.",
)
async def list_clients(
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> list[ClientResponse]:
    clients = await ClientRepository(session).list(offset=offset, limit=limit)
    return [_to_client_response(client) for client in clients]


@router.get(
    "/{client_id:int}",
    response_model=ClientResponse,
    summary="Detalhar cliente",
    description="Retorna os dados completos de um cliente (admin).",
)
async def get_client(
    client_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> ClientResponse:
    client = await _get_client_or_404(session, client_id)
    return _to_client_response(client)


@router.patch(
    "/{client_id:int}",
    response_model=ClientResponse,
    summary="Atualizar cliente",
    description="Atualiza parcialmente um cliente (admin).",
)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> ClientResponse:
    client = await _get_client_or_404(session, client_id)
    try:
        updated = await ClientRepository(session).update(
            client,
            **payload.model_dump(exclude_unset=True),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF de cliente já cadastrado.",
        ) from exc
    return _to_client_response(updated)


@router.delete(
    "/{client_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir cliente",
    description="Exclui um cliente (admin).",
)
async def delete_client(
    client_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    client = await _get_client_or_404(session, client_id)
    await ClientRepository(session).delete(client)
    await session.commit()


@router.get(
    "/me",
    response_model=ClientResponse,
    summary="Meu perfil de cliente",
    description="Retorna o cliente associado ao token autenticado.",
)
async def get_me(
    current_user: User = Depends(require_roles(UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> ClientResponse:
    if current_user.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não vinculado."
        )
    client = await _get_client_or_404(session, current_user.client_id)
    return _to_client_response(client, cpf_override=client.cpf or current_user.cpf)


@router.patch(
    "/me",
    response_model=ClientResponse,
    summary="Atualizar meu perfil",
    description="Permite ao cliente atualizar somente seu próprio cadastro.",
)
async def update_me(
    payload: ClientUpdate,
    current_user: User = Depends(require_roles(UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> ClientResponse:
    if current_user.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não vinculado."
        )
    client = await _get_client_or_404(session, current_user.client_id)
    try:
        updated = await ClientRepository(session).update(
            client,
            **payload.model_dump(exclude_unset=True),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF de cliente já cadastrado.",
        ) from exc
    return _to_client_response(updated, cpf_override=updated.cpf or current_user.cpf)


@router.post(
    "/{client_id:int}/photo",
    response_model=PhotoUploadResponse,
    summary="Upload de foto do cliente",
    description="Admin pode enviar para qualquer cliente; cliente só para si.",
)
async def upload_client_photo(
    client_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> PhotoUploadResponse:
    client = await _get_client_or_404(session, client_id)
    if not is_admin(current_user):
        check_ownership(client.id, current_user)

    relative_path = await save_image_upload(
        file, resource_folder=f"clients/{client.id}"
    )
    client.photo_url = relative_path
    await session.commit()
    await session.refresh(client)
    return PhotoUploadResponse(photo_url=relative_path)
