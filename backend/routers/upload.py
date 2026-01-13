import os
import uuid
import shutil

from fastapi import APIRouter, File, UploadFile, HTTPException, status

from config import settings


def get_router(upload_dir: str) -> APIRouter:
    router = APIRouter()

    @router.post(f"{settings.api_prefix}/upload")
    async def upload_file(file: UploadFile = File(...)):
        """
        Upload a file (image) and return its URL
        """
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}",
            )

        return {"url": f"/uploads/{unique_filename}"}

    return router
