from datetime import datetime, timezone
from pathlib import PurePath
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.ImageAsset import ImageAsset
from src.models.User import User
from src.storage.StorjStorage import StorjStorage

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


class UploadController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        storage: Annotated[StorjStorage, Depends(StorjStorage)],
    ):
        self.db = db
        self.storage = storage

    async def create_profile_image_upload(
        self,
        user_id: int,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> dict:
        extension = ALLOWED_IMAGE_TYPES.get(content_type)
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Profile images must be JPEG, PNG, or WebP.",
            )
        if size_bytes < 1 or size_bytes > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Profile images must be no larger than 5 MB.",
            )

        object_key = f"profile-images/{user_id}/{uuid4().hex}.{extension}"
        upload_url = await self.storage.create_upload_url(object_key, content_type)

        image = ImageAsset(
            user_id=user_id,
            object_key=object_key,
            original_filename=PurePath(filename).name[:255],
            content_type=content_type,
            size_bytes=size_bytes,
            status="PENDING",
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)

        return {
            "message": "Image upload authorized",
            "data": {
                "image_id": image.id,
                "object_key": image.object_key,
                "upload_url": upload_url,
                "expires_in": 60,
            },
        }

    async def complete_profile_image_upload(
        self,
        user_id: int,
        image_id: int,
    ) -> dict:
        image = await self.db.get(ImageAsset, image_id)
        if image is None or image.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image upload not found.",
            )
        if image.status == "READY" and image.is_profile_image:
            return {
                "message": "Profile image is already active",
                "data": {
                    "image_id": image.id,
                    "image_url": await self.storage.get_image_url(
                        image.object_key
                    ),
                },
            }
        if image.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This image upload cannot be completed.",
            )

        await self.storage.verify_upload(
            image.object_key,
            image.content_type,
            image.size_bytes,
        )

        await self.db.scalar(
            select(User.id)
            .where(User.id == user_id)
            .with_for_update()
        )
        await self.db.execute(
            update(ImageAsset)
            .where(
                ImageAsset.user_id == user_id,
                ImageAsset.is_profile_image.is_(True),
            )
            .values(is_profile_image=False)
        )
        image.status = "READY"
        image.is_profile_image = True
        image.public_url = self.storage.public_url(image.object_key)
        image.updated_at = datetime.now(timezone.utc)
        await self.db.commit()

        return {
            "message": "Profile image updated successfully",
            "data": {
                "image_id": image.id,
                "image_url": await self.storage.get_image_url(
                    image.object_key
                ),
            },
        }
