import os
import time
import tracemalloc

from fastapi import APIRouter

from metaway_api.interfaces.schemas import HealthResponse, MetricsResponse

router = APIRouter(tags=["health"])
_START_TIME = time.monotonic()

try:
    import resource
except ImportError:  # pragma: no cover - apenas em plataformas sem módulo resource
    resource = None


def _memory_mb() -> float:
    if resource is not None:
        memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if memory > 1024 * 1024 * 1024:
            return round(memory / (1024 * 1024), 2)
        return round(memory / 1024, 2)

    if not tracemalloc.is_tracing():
        tracemalloc.start()
    current, _ = tracemalloc.get_traced_memory()
    return round(current / (1024 * 1024), 2)


def _cpu_percent() -> float:
    try:
        load_avg = os.getloadavg()[0]
    except (AttributeError, OSError):
        return 0.0
    cpu_count = max(os.cpu_count() or 1, 1)
    return round((load_avg / cpu_count) * 100, 2)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Healthcheck",
    description="Retorna status básico para verificar disponibilidade da API.",
)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Métricas de processo",
    description="Retorna uptime, uso aproximado de memória e CPU do processo da API.",
)
async def metrics() -> MetricsResponse:
    return MetricsResponse(
        uptime_seconds=round(time.monotonic() - _START_TIME, 2),
        memory_mb=_memory_mb(),
        cpu_percent=_cpu_percent(),
    )
