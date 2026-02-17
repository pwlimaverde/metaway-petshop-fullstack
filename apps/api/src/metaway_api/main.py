from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from metaway_api.infra.database import AsyncSessionLocal
from metaway_api.infra.seed import seed_initial_data
from metaway_api.interfaces.routers.addresses import router as addresses_router
from metaway_api.interfaces.routers.appointments import router as appointments_router
from metaway_api.interfaces.routers.auth import router as auth_router
from metaway_api.interfaces.routers.breeds import router as breeds_router
from metaway_api.interfaces.routers.clients import router as clients_router
from metaway_api.interfaces.routers.contacts import router as contacts_router
from metaway_api.interfaces.routers.files import router as files_router
from metaway_api.interfaces.routers.health import router as health_router
from metaway_api.interfaces.routers.pets import router as pets_router
from metaway_api.interfaces.routers.users import router as users_router
from metaway_api.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "Auth", "description": "Autenticação e emissão de token JWT."},
    {"name": "Users", "description": "Gestão de usuários (somente admin)."},
    {"name": "Clients", "description": "Cadastro de clientes e endpoints /me."},
    {"name": "Addresses", "description": "Endereços de clientes com ownership."},
    {"name": "Contacts", "description": "Contatos de clientes com ownership."},
    {"name": "Breeds", "description": "Cadastro de raças de pets."},
    {"name": "Pets", "description": "Cadastro de pets com ownership."},
    {"name": "Appointments", "description": "Atendimentos vinculados aos pets."},
    {"name": "Files", "description": "Acesso a arquivos de upload."},
    {"name": "health", "description": "Healthcheck e métricas."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    except OSError:  # pragma: no cover - depende do ambiente de execução
        logger.exception("Não foi possível preparar diretório de uploads.")
    if settings.run_seed_on_startup:
        try:
            async with AsyncSessionLocal() as session:
                await seed_initial_data(session, only_if_empty=True)
        except Exception:  # pragma: no cover - fallback para ambientes sem banco ativo
            logger.exception("Falha ao executar seed inicial no startup.")
    yield


app = FastAPI(
    title="Metaway Petshop API",
    version="1.0.0",
    description="API para gestão de clientes, pets, raças e atendimentos.",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(clients_router, prefix=settings.api_prefix)
app.include_router(addresses_router, prefix=settings.api_prefix)
app.include_router(contacts_router, prefix=settings.api_prefix)
app.include_router(breeds_router, prefix=settings.api_prefix)
app.include_router(pets_router, prefix=settings.api_prefix)
app.include_router(appointments_router, prefix=settings.api_prefix)
app.include_router(files_router, prefix=settings.api_prefix)
