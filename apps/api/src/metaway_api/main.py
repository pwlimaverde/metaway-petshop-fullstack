from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from metaway_api.interfaces.routers.health import router as health_router
from metaway_api.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Metaway Petshop API",
    version="0.1.0",
    description="API para gestão de clientes, pets, raças e atendimentos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
