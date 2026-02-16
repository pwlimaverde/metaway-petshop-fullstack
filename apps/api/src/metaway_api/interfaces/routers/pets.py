from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import check_ownership, is_admin, require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.file_storage import save_image_upload
from metaway_api.infra.models import Breed, Client, Pet, User
from metaway_api.infra.repositories import PetRepository
from metaway_api.interfaces.schemas import (
    PetCreate,
    PetResponse,
    PetUpdate,
    PhotoUploadResponse,
)

router = APIRouter(prefix="/pets", tags=["Pets"])


async def _get_pet_or_404(session: AsyncSession, pet_id: int) -> Pet:
    pet = await PetRepository(session).get_by_id(pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado."
        )
    return pet


async def _ensure_foreign_keys(
    session: AsyncSession, *, client_id: int, breed_id: int
) -> None:
    if await session.get(Client, client_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado."
        )
    if await session.get(Breed, breed_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raça não encontrada."
        )


@router.post(
    "",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pet",
    description="Cria pet vinculado a cliente e raça (admin).",
)
async def create_pet(
    payload: PetCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> PetResponse:
    await _ensure_foreign_keys(
        session, client_id=payload.client_id, breed_id=payload.breed_id
    )
    pet = await PetRepository(session).create(**payload.model_dump())
    await session.commit()
    return PetResponse.model_validate(pet)


@router.get(
    "",
    response_model=list[PetResponse],
    summary="Listar pets",
    description="Admin lista todos; cliente lista apenas pets próprios.",
)
async def list_pets(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> list[PetResponse]:
    repository = PetRepository(session)
    if is_admin(current_user):
        pets = await repository.list(offset=offset, limit=limit)
    else:
        if current_user.client_id is None:
            return []
        pets = await repository.list_by_client_id(
            current_user.client_id, offset=offset, limit=limit
        )
    return [PetResponse.model_validate(pet) for pet in pets]


@router.get(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Detalhar pet",
    description="Admin consulta qualquer pet; cliente apenas pet próprio.",
)
async def get_pet(
    pet_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> PetResponse:
    pet = await _get_pet_or_404(session, pet_id)
    if not is_admin(current_user):
        check_ownership(pet.client_id, current_user)
    return PetResponse.model_validate(pet)


@router.patch(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Atualizar pet",
    description="Admin atualiza qualquer pet; cliente atualiza apenas pet próprio.",
)
async def update_pet(
    pet_id: int,
    payload: PetUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> PetResponse:
    pet = await _get_pet_or_404(session, pet_id)
    if not is_admin(current_user):
        check_ownership(pet.client_id, current_user)
        if (
            payload.client_id is not None
            and payload.client_id != current_user.client_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cliente não pode transferir pet para outro cliente.",
            )

    next_client_id = (
        payload.client_id if payload.client_id is not None else pet.client_id
    )
    next_breed_id = payload.breed_id if payload.breed_id is not None else pet.breed_id
    await _ensure_foreign_keys(
        session, client_id=next_client_id, breed_id=next_breed_id
    )

    try:
        updated = await PetRepository(session).update(
            pet,
            **payload.model_dump(exclude_unset=True),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar o pet.",
        ) from exc
    return PetResponse.model_validate(updated)


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir pet",
    description="Exclui pet (admin).",
)
async def delete_pet(
    pet_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    pet = await _get_pet_or_404(session, pet_id)
    await PetRepository(session).delete(pet)
    await session.commit()


@router.post(
    "/{pet_id}/photo",
    response_model=PhotoUploadResponse,
    summary="Upload de foto do pet",
    description="Admin pode enviar para qualquer pet; cliente só para pet próprio.",
)
async def upload_pet_photo(
    pet_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> PhotoUploadResponse:
    pet = await _get_pet_or_404(session, pet_id)
    if not is_admin(current_user):
        check_ownership(pet.client_id, current_user)

    relative_path = await save_image_upload(file, resource_folder=f"pets/{pet.id}")
    pet.photo_url = relative_path
    await session.commit()
    await session.refresh(pet)
    return PhotoUploadResponse(photo_url=relative_path)
