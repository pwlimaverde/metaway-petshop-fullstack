from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import Breed, User
from metaway_api.infra.repositories import BreedRepository
from metaway_api.interfaces.schemas import BreedCreate, BreedResponse, BreedUpdate

router = APIRouter(prefix="/breeds", tags=["Breeds"])


async def _get_breed_or_404(session: AsyncSession, breed_id: int) -> Breed:
    breed = await BreedRepository(session).get_by_id(breed_id)
    if breed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Raça não encontrada."
        )
    return breed


@router.post(
    "",
    response_model=BreedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar raça",
    description="Cria uma raça de pet (admin).",
)
async def create_breed(
    payload: BreedCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> BreedResponse:
    try:
        breed = await BreedRepository(session).create(**payload.model_dump())
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição de raça já cadastrada.",
        ) from exc
    return BreedResponse.model_validate(breed)


@router.get(
    "",
    response_model=list[BreedResponse],
    summary="Listar raças",
    description="Lista raças disponíveis. Permitido para admin e cliente.",
)
async def list_breeds(
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> list[BreedResponse]:
    breeds = await BreedRepository(session).list(offset=offset, limit=limit)
    return [BreedResponse.model_validate(breed) for breed in breeds]


@router.get(
    "/{breed_id}",
    response_model=BreedResponse,
    summary="Detalhar raça",
    description="Retorna detalhes de uma raça. Permitido para admin e cliente.",
)
async def get_breed(
    breed_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> BreedResponse:
    breed = await _get_breed_or_404(session, breed_id)
    return BreedResponse.model_validate(breed)


@router.patch(
    "/{breed_id}",
    response_model=BreedResponse,
    summary="Atualizar raça",
    description="Atualiza parcialmente uma raça (admin).",
)
async def update_breed(
    breed_id: int,
    payload: BreedUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> BreedResponse:
    breed = await _get_breed_or_404(session, breed_id)
    try:
        updated = await BreedRepository(session).update(
            breed,
            **payload.model_dump(exclude_unset=True),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar a raça.",
        ) from exc
    return BreedResponse.model_validate(updated)


@router.delete(
    "/{breed_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir raça",
    description="Exclui uma raça (admin).",
)
async def delete_breed(
    breed_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    breed = await _get_breed_or_404(session, breed_id)
    await BreedRepository(session).delete(breed)
    await session.commit()
