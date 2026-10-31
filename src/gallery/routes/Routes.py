from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from src.common.token.JwtService import JwtTokenService
from src.gallery.controller.Controller import GalleryController
from src.middlewares.authorization import require_access_token


class AdminGalleryUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(gt=0, le=5 * 1024 * 1024)
    is_premium: bool = False


class GalleryImageUpdate(BaseModel):
    is_premium: bool


class BulkDeleteRequest(BaseModel):
    image_ids: list[int] = Field(min_length=1, max_length=100)


def _optional_user_id(
    request: Request,
    token_service: Annotated[JwtTokenService, Depends(JwtTokenService)],
) -> int | None:
    token = request.cookies.get("access_token")
    if token is None:
        return None
    try:
        payload = token_service.verify(token)
        return int(payload["user_id"])
    except (ValueError, KeyError, TypeError):
        return None


def getPublicRouter() -> APIRouter:
    router = APIRouter(prefix="/gallery", tags=["Gallery"])

    @router.get("")
    async def browse_gallery(
        controller: Annotated[GalleryController, Depends(GalleryController)],
        offset: Annotated[int, Query(ge=0)] = 0,
        user_id: Annotated[int | None, Depends(_optional_user_id)] = None,
    ):
        return await controller.browse(offset=offset, user_id=user_id)

    return router


def getAdminRouter() -> APIRouter:
    router = APIRouter(prefix="/gallery", tags=["Admin gallery"])

    @router.get("")
    async def list_images(
        controller: Annotated[GalleryController, Depends(GalleryController)],
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 24,
    ):
        return await controller.list_admin(page=page, page_size=page_size)

    @router.post("/presign", status_code=201)
    async def presign_image(
        payload: AdminGalleryUploadRequest,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[GalleryController, Depends(GalleryController)],
    ):
        return await controller.create_upload(
            admin_id=int(current_user["user_id"]),
            filename=payload.filename,
            content_type=payload.content_type,
            size_bytes=payload.size_bytes,
            is_premium=payload.is_premium,
        )

    @router.post("/{image_id}/complete")
    async def complete_upload(
        image_id: int,
        controller: Annotated[GalleryController, Depends(GalleryController)],
    ):
        return await controller.complete_upload(image_id=image_id)

    @router.patch("/{image_id}")
    async def update_image(
        image_id: int,
        payload: GalleryImageUpdate,
        controller: Annotated[GalleryController, Depends(GalleryController)],
    ):
        return await controller.set_premium(
            image_id=image_id,
            is_premium=payload.is_premium,
        )

    @router.delete("/{image_id}")
    async def delete_image(
        image_id: int,
        controller: Annotated[GalleryController, Depends(GalleryController)],
    ):
        return await controller.delete_one(image_id=image_id)

    @router.post("/bulk-delete")
    async def delete_images(
        payload: BulkDeleteRequest,
        controller: Annotated[GalleryController, Depends(GalleryController)],
    ):
        return await controller.delete_many(image_ids=payload.image_ids)

    return router
