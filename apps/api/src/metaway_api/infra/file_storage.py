from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError

from metaway_api.settings import get_settings

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
NORMALIZED_IMAGE_SIZE = (512, 512)


def _normalize_image(content: bytes, content_type: str) -> bytes:
    try:
        with Image.open(BytesIO(content)) as source:
            fitted = ImageOps.fit(
                source,
                NORMALIZED_IMAGE_SIZE,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            output = BytesIO()
            if content_type == "image/png":
                fitted.convert("RGBA").save(output, format="PNG", optimize=True)
            else:
                fitted.convert("RGB").save(
                    output, format="JPEG", optimize=True, quality=90
                )
            return output.getvalue()
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Use JPEG ou PNG.",
        ) from exc


def _storage_root() -> Path:
    root = Path(get_settings().upload_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


async def save_image_upload(file: UploadFile, *, resource_folder: str) -> str:
    extension = ALLOWED_IMAGE_CONTENT_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Use JPEG ou PNG.",
        )

    content = await file.read()
    max_size_bytes = get_settings().upload_max_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo excede o tamanho máximo permitido.",
        )
    normalized_content = _normalize_image(content, file.content_type or "")

    root = _storage_root()
    filename = f"{uuid4().hex}{extension}"
    relative_path = Path(resource_folder) / filename
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(normalized_content)
    return relative_path.as_posix()


def resolve_storage_file(relative_path: str) -> Path:
    root = _storage_root().resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado.",
        )
    if not target.exists() or not target.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado.",
        )
    return target
