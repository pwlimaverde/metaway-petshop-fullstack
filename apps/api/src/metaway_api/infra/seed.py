from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metaway_api.domain.enums import UserRole
from metaway_api.domain.validators import validate_cpf
from metaway_api.infra.models import Breed, User
from metaway_api.infra.security import hash_password, validate_password_strength
from metaway_api.settings import get_settings

DEFAULT_BREEDS = [
    "Labrador",
    "Golden Retriever",
    "Poodle",
    "Bulldog",
    "Shih Tzu",
    "Pastor Alemão",
    "Pinscher",
    "Vira-lata",
]


async def seed_initial_data(session: AsyncSession) -> None:
    settings = get_settings()
    admin_seed_cpf = validate_cpf(settings.admin_seed_cpf)
    validate_password_strength(settings.admin_seed_password)
    has_changes = False

    result = await session.execute(select(User).where(User.cpf == admin_seed_cpf))
    admin_user = result.scalar_one_or_none()
    if admin_user is None:
        session.add(
            User(
                cpf=admin_seed_cpf,
                name=settings.admin_seed_name,
                role=UserRole.ADMIN,
                password_hash=hash_password(settings.admin_seed_password),
            )
        )
        has_changes = True

    existing_breeds_rows = await session.execute(select(Breed.descricao))
    existing_breeds = set(existing_breeds_rows.scalars().all())
    for breed in DEFAULT_BREEDS:
        if breed not in existing_breeds:
            session.add(Breed(descricao=breed))
            has_changes = True

    if has_changes:
        await session.commit()
