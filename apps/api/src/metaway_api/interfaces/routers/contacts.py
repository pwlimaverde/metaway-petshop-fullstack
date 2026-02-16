from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import check_ownership, is_admin, require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import Client, Contact, User
from metaway_api.infra.repositories import ContactRepository
from metaway_api.interfaces.schemas import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(tags=["Contacts"])


async def _get_contact_or_404(session: AsyncSession, contact_id: int) -> Contact:
    contact = await ContactRepository(session).get_by_id(contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contato não encontrado."
        )
    return contact


async def _ensure_client_exists(session: AsyncSession, client_id: int) -> None:
    if await session.get(Client, client_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )


@router.post(
    "/clients/{client_id:int}/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar contato de cliente",
    description="Cria contato para um cliente específico (admin).",
)
async def create_contact_for_client(
    client_id: int,
    payload: ContactCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> ContactResponse:
    await _ensure_client_exists(session, client_id)
    contact = await ContactRepository(session).create(
        client_id=client_id, **payload.model_dump()
    )
    await session.commit()
    return ContactResponse.model_validate(contact)


@router.get(
    "/clients/{client_id:int}/contacts",
    response_model=list[ContactResponse],
    summary="Listar contatos de cliente",
    description="Lista contatos de um cliente específico (admin).",
)
async def list_contacts_for_client(
    client_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> list[ContactResponse]:
    await _ensure_client_exists(session, client_id)
    contacts = await ContactRepository(session).list_by_client_id(client_id)
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.get(
    "/clients/me/contacts",
    response_model=list[ContactResponse],
    summary="Listar meus contatos",
    description="Lista contatos do cliente autenticado.",
)
async def list_my_contacts(
    current_user: User = Depends(require_roles(UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> list[ContactResponse]:
    if current_user.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não vinculado."
        )
    contacts = await ContactRepository(session).list_by_client_id(
        current_user.client_id
    )
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.patch(
    "/contacts/{contact_id}",
    response_model=ContactResponse,
    summary="Atualizar contato",
    description="Admin pode atualizar qualquer contato; cliente apenas os próprios.",
)
async def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> ContactResponse:
    contact = await _get_contact_or_404(session, contact_id)
    if not is_admin(current_user):
        check_ownership(contact.client_id, current_user)

    updated = await ContactRepository(session).update(
        contact,
        **payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    return ContactResponse.model_validate(updated)


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir contato",
    description="Exclui contato (admin).",
)
async def delete_contact(
    contact_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    contact = await _get_contact_or_404(session, contact_id)
    await ContactRepository(session).delete(contact)
    await session.commit()
