from fastapi import APIRouter
from fastapi.responses import FileResponse

from metaway_api.infra.file_storage import resolve_storage_file

router = APIRouter(prefix="/files", tags=["Files"])


@router.get(
    "/{file_path:path}",
    summary="Servir arquivo",
    description="Retorna arquivo armazenado no diretório de uploads.",
)
async def serve_file(file_path: str) -> FileResponse:
    resolved = resolve_storage_file(file_path)
    return FileResponse(path=resolved)
