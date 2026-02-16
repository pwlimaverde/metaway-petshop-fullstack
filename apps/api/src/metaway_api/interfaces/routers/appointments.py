from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.infra.auth import check_ownership, is_admin, require_roles
from metaway_api.infra.database import get_db_session
from metaway_api.infra.models import Appointment, Pet, User
from metaway_api.infra.repositories import AppointmentRepository, PetRepository
from metaway_api.interfaces.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


async def _get_appointment_or_404(
    session: AsyncSession, appointment_id: int
) -> Appointment:
    appointment = await AppointmentRepository(session).get_by_id(appointment_id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atendimento não encontrado.",
        )
    return appointment


async def _ensure_pet_exists(session: AsyncSession, pet_id: int) -> Pet:
    pet = await session.get(Pet, pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet não encontrado."
        )
    return pet


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar atendimento",
    description="Cria atendimento para um pet (admin).",
)
async def create_appointment(
    payload: AppointmentCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    await _ensure_pet_exists(session, payload.pet_id)
    appointment = await AppointmentRepository(session).create(**payload.model_dump())
    await session.commit()
    return AppointmentResponse.model_validate(appointment)


@router.get(
    "",
    response_model=list[AppointmentResponse],
    summary="Listar atendimentos",
    description=(
        "Admin lista todos; cliente lista apenas atendimentos dos próprios pets."
    ),
)
async def list_appointments(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> list[AppointmentResponse]:
    repository = AppointmentRepository(session)
    if is_admin(current_user):
        appointments = await repository.list(offset=offset, limit=limit)
    else:
        if current_user.client_id is None:
            return []
        pets = await PetRepository(session).list_by_client_id(
            current_user.client_id, offset=0, limit=500
        )
        pet_ids = [pet.id for pet in pets]
        appointments = await repository.list_by_pet_ids(
            pet_ids, offset=offset, limit=limit
        )
    return [
        AppointmentResponse.model_validate(appointment) for appointment in appointments
    ]


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Detalhar atendimento",
    description="Admin consulta qualquer atendimento; cliente apenas de seus pets.",
)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await _get_appointment_or_404(session, appointment_id)
    if not is_admin(current_user):
        check_ownership(appointment.pet.client_id, current_user)
    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Atualizar atendimento",
    description="Admin atualiza qualquer atendimento; cliente apenas de seus pets.",
)
async def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CLIENTE)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await _get_appointment_or_404(session, appointment_id)
    if not is_admin(current_user):
        check_ownership(appointment.pet.client_id, current_user)

    next_pet_id = payload.pet_id if payload.pet_id is not None else appointment.pet_id
    target_pet = await _ensure_pet_exists(session, next_pet_id)
    if not is_admin(current_user):
        check_ownership(target_pet.client_id, current_user)

    try:
        updated = await AppointmentRepository(session).update(
            appointment,
            **payload.model_dump(exclude_unset=True),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar o atendimento.",
        ) from exc

    return AppointmentResponse.model_validate(updated)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir atendimento",
    description="Exclui atendimento (admin).",
)
async def delete_appointment(
    appointment_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    appointment = await _get_appointment_or_404(session, appointment_id)
    await AppointmentRepository(session).delete(appointment)
    await session.commit()
