from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.middlewares.authorization import require_access_token
from src.uploads.controller.Controller import UploadController


class PresignProfileImageRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(gt=0, le=5 * 1024 * 1024)


def getRouter() -> APIRouter:
    router = APIRouter(prefix="/uploads", tags=["Image uploads"])

    @router.post("/presign", status_code=201)
    async def presign_profile_image(
        payload: PresignProfileImageRequest,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[UploadController, Depends(UploadController)],
    ):
        return await controller.create_profile_image_upload(
            user_id=int(current_user["user_id"]),
            filename=payload.filename,
            content_type=payload.content_type,
            size_bytes=payload.size_bytes,
        )

    @router.post("/{image_id}/complete")
    async def complete_profile_image(
        image_id: int,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[UploadController, Depends(UploadController)],
    ):
        return await controller.complete_profile_image_upload(
            user_id=int(current_user["user_id"]),
            image_id=image_id,
        )

    return router
