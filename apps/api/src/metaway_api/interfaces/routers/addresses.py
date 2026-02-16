from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import check_ownership, is_admin, require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import Address, Client, User
from metaway_api.infra.repositories import AddressRepository
from metaway_api.interfaces.schemas import AddressCreate, AddressResponse, AddressUpdate

router = APIRouter(tags=["Addresses"])


async def _get_address_or_404(session: AsyncSession, address_id: int) -> Address:
    address = await AddressRepository(session).get_by_id(address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Endereço não encontrado."
        )
    return address


async def _ensure_client_exists(session: AsyncSession, client_id: int) -> None:
    if await session.get(Client, client_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )


@router.post(
    "/clients/{client_id:int}/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar endereço de cliente",
    description="Cria endereço para um cliente específico (admin).",
)
async def create_address_for_client(
    client_id: int,
    payload: AddressCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> AddressResponse:
    await _ensure_client_exists(session, client_id)
    address = await AddressRepository(session).create(
        client_id=client_id, **payload.model_dump()
    )
    await session.commit()
    return AddressResponse.model_validate(address)


@router.get(
    "/clients/{client_id:int}/addresses",
    response_model=list[AddressResponse],
    summary="Listar endereços de cliente",
    description="Lista endereços de um cliente específico (admin).",
)
async def list_addresses_for_client(
    client_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> list[AddressResponse]:
    await _ensure_client_exists(session, client_id)
    addresses = await AddressRepository(session).list_by_client_id(client_id)
    return [AddressResponse.model_validate(address) for address in addresses]


@router.get(
    "/clients/me/addresses",
    response_model=list[AddressResponse],
    summary="Listar meus endereços",
    description="Lista os endereços do cliente autenticado.",
)
async def list_my_addresses(
    current_user: User = Depends(require_roles(UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> list[AddressResponse]:
    if current_user.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não vinculado."
        )
    addresses = await AddressRepository(session).list_by_client_id(
        current_user.client_id
    )
    return [AddressResponse.model_validate(address) for address in addresses]


@router.patch(
    "/addresses/{address_id}",
    response_model=AddressResponse,
    summary="Atualizar endereço",
    description="Admin pode atualizar qualquer endereço; cliente apenas os próprios.",
)
async def update_address(
    address_id: int,
    payload: AddressUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> AddressResponse:
    address = await _get_address_or_404(session, address_id)
    if not is_admin(current_user):
        check_ownership(address.client_id, current_user)

    updated = await AddressRepository(session).update(
        address,
        **payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    return AddressResponse.model_validate(updated)


@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir endereço",
    description="Exclui endereço (admin).",
)
async def delete_address(
    address_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    address = await _get_address_or_404(session, address_id)
    await AddressRepository(session).delete(address)
    await session.commit()
