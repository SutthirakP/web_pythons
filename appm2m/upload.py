"""Product image upload, based on upload/main.py.

Flow used by the catalog page:
  1. POST /upload (multipart, field "file")  -> {"filename": "<uuid>.jpg", "url": "/file/<uuid>.jpg"}
  2. send that filename as "image" in POST /products/ or PUT /products/{id}
  3. show it with <img src="http://127.0.0.1:8002/file/<uuid>.jpg">
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from .auth import get_current_user

router = APIRouter(tags=["upload"])

# Anchored to appm2m/ like catalog.db, so it doesn't depend on where uvicorn is started.
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def image_path(filename: str) -> Path | None:
    """Path of an uploaded file, or None if the name is unsafe or the file is missing.

    Path(name).name == name blocks names like "../main.py" from escaping uploads/.
    """
    if not filename or Path(filename).name != filename:
        return None
    path = UPLOAD_DIR / filename
    return path if path.is_file() else None


def delete_image(filename: str | None) -> None:
    path = image_path(filename) if filename else None
    if path:
        path.unlink(missing_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile, current_user: dict = Depends(get_current_user)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS or not (file.content_type or "").startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only image files are allowed ({', '.join(sorted(ALLOWED_EXTENSIONS))})",
        )

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Image must be 5 MB or smaller",
        )

    # random name: two uploads called "photo.jpg" never overwrite each other
    name = f"{uuid.uuid4()}{ext}"
    (UPLOAD_DIR / name).write_bytes(data)
    return {"filename": name, "url": f"/file/{name}"}


@router.get("/file/{filename}")
async def get_file(filename: str):
    path = image_path(filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(path)
