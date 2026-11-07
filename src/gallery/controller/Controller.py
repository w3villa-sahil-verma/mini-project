import asyncio
from datetime import datetime, timezone
from pathlib import PurePath
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.gallery.services.DownloadAccessService import download_access_expires_at
from src.gallery.services.ImagePreviewService import create_gallery_preview
from src.models.ImageAsset import ImageAsset
from src.models.Plan import Plan
from src.models.Subscription import Subscription
from src.models.User import User
from src.storage.StorjStorage import StorjStorage
from src.uploads.controller.Controller import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE_BYTES

GALLERY_PAGE_SIZE = 24
MAX_BULK_DELETE = 100


class GalleryController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        storage: Annotated[StorjStorage, Depends(StorjStorage)],
    ):
        self.db = db
        self.storage = storage

    async def browse(self, *, offset: int, user_id: int | None) -> dict:
        premium_expires_at = await self._premium_access_expires_at(user_id)
        has_premium_access = premium_expires_at is not None
        download_expires_at = await self._download_access_expires_at(user_id)
        query = select(ImageAsset).where(
            ImageAsset.is_gallery.is_(True),
            ImageAsset.status == "READY",
        )

        images = await self.db.scalars(
            query.order_by(ImageAsset.created_at.desc(), ImageAsset.id.desc())
            .offset(offset)
            .limit(GALLERY_PAGE_SIZE + 1)
        )
        rows = images.all()
        has_more = len(rows) > GALLERY_PAGE_SIZE
        page = rows[:GALLERY_PAGE_SIZE]

        payload = []
        for image in page:
            preview_key = await self._ensure_gallery_preview(image)
            image_url = await self.storage.get_image_url(
                preview_key,
                use_public_url=False,
            )
            payload.append(
                {
                    "id": image.id,
                    "is_premium": image.is_premium,
                    "filename": image.original_filename,
                    "image_url": image_url,
                    "can_download": download_expires_at is not None,
                }
            )

        return {
            "message": "Gallery images retrieved successfully",
            "data": {
                "items": payload,
                "has_more": has_more,
                "next_offset": offset + len(page),
                "has_premium_access": has_premium_access,
                "download_access_expires_at": download_expires_at,
            },
        }

    async def create_download(self, *, image_id: int, user_id: int) -> dict:
        image = await self._get_gallery_image(image_id)
        if image.status != "READY":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery image not found.",
            )

        access_expires_at = await self._download_access_expires_at(user_id)
        if access_expires_at is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="An active Silver or Gold membership is required to download high-resolution images.",
            )

        remaining_seconds = int(
            (access_expires_at - datetime.now(timezone.utc)).total_seconds()
        )
        if remaining_seconds < 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your high-resolution download access has expired.",
            )

        download_url = await self.storage.get_image_url(
            image.object_key,
            expires_in=min(10800, remaining_seconds),
            use_public_url=False,
            download_filename=image.original_filename,
        )
        return {
            "message": "High-resolution download authorized",
            "data": {
                "download_url": download_url,
                "expires_at": access_expires_at,
            },
        }

    async def list_admin(self, *, page: int, page_size: int) -> dict:
        total = await self.db.scalar(
            select(func.count(ImageAsset.id)).where(
                ImageAsset.is_gallery.is_(True),
                ImageAsset.status.in_(("READY", "PENDING")),
            )
        )
        result = await self.db.scalars(
            select(ImageAsset)
            .where(
                ImageAsset.is_gallery.is_(True),
                ImageAsset.status.in_(("READY", "PENDING")),
            )
            .order_by(ImageAsset.created_at.desc(), ImageAsset.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = []
        for image in result.all():
            items.append(
                {
                    **self._serialize(image),
                    "image_url": (
                        await self.storage.get_image_url(
                            image.object_key,
                            use_public_url=False,
                        )
                        if image.status == "READY"
                        else None
                    ),
                }
            )

        return {
            "message": "Gallery images retrieved successfully",
            "data": {
                "items": items,
                "total": int(total or 0),
                "page": page,
                "page_size": page_size,
                "total_pages": (int(total or 0) + page_size - 1) // page_size,
            },
        }

    async def create_upload(
        self,
        *,
        admin_id: int,
        filename: str,
        content_type: str,
        size_bytes: int,
        is_premium: bool,
    ) -> dict:
        extension = ALLOWED_IMAGE_TYPES.get(content_type)
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Gallery images must be JPEG, PNG, or WebP.",
            )
        if size_bytes < 1 or size_bytes > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Gallery images must be no larger than 5 MB.",
            )

        object_key = f"gallery/{admin_id}/{uuid4().hex}.{extension}"
        upload_url = await self.storage.create_upload_url(object_key, content_type)
        image = ImageAsset(
            user_id=admin_id,
            object_key=object_key,
            original_filename=PurePath(filename).name[:255],
            content_type=content_type,
            size_bytes=size_bytes,
            status="PENDING",
            is_gallery=True,
            is_premium=is_premium,
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)

        return {
            "message": "Gallery image upload authorized",
            "data": {
                "image_id": image.id,
                "upload_url": upload_url,
                "expires_in": 60,
            },
        }

    async def complete_upload(self, *, image_id: int) -> dict:
        image = await self._get_gallery_image(image_id)
        if image.status == "READY":
            return {
                "message": "Gallery image is already ready",
                "data": self._serialize(image),
            }
        if image.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This gallery image upload cannot be completed.",
            )

        await self.storage.verify_upload(
            image.object_key,
            image.content_type,
            image.size_bytes,
        )
        await self._generate_gallery_preview(image)
        image.status = "READY"
        image.public_url = None
        image.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(image)
        return {
            "message": "Gallery image uploaded successfully",
            "data": self._serialize(image),
        }

    async def set_premium(self, *, image_id: int, is_premium: bool) -> dict:
        image = await self._get_gallery_image(image_id)
        image.is_premium = is_premium
        if image.status == "READY":
            await self._generate_gallery_preview(image)
        image.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return {
            "message": "Gallery image updated successfully",
            "data": self._serialize(image),
        }

    async def delete_one(self, *, image_id: int) -> dict:
        image = await self._get_gallery_image(image_id)
        await self.storage.delete_object(self._preview_object_key(image.id))
        await self.storage.delete_object(image.object_key)
        await self.db.delete(image)
        await self.db.commit()
        return {"message": "Gallery image deleted successfully", "data": {"id": image_id}}

    async def delete_many(self, *, image_ids: list[int]) -> dict:
        unique_ids = list(dict.fromkeys(image_ids))
        if not unique_ids or len(unique_ids) > MAX_BULK_DELETE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Select between 1 and {MAX_BULK_DELETE} images.",
            )

        result = await self.db.scalars(
            select(ImageAsset).where(
                ImageAsset.id.in_(unique_ids),
                ImageAsset.is_gallery.is_(True),
            )
        )
        images = result.all()
        if len(images) != len(unique_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more selected gallery images were not found.",
            )

        for image in images:
            await self.storage.delete_object(self._preview_object_key(image.id))
            await self.storage.delete_object(image.object_key)
        await self.db.execute(
            update(ImageAsset)
            .where(
                ImageAsset.id.in_(unique_ids),
                ImageAsset.is_gallery.is_(True),
            )
            .values(status="DELETED", is_profile_image=False)
        )
        await self.db.commit()
        return {
            "message": f"Deleted {len(unique_ids)} gallery images successfully",
            "data": {"deleted_ids": unique_ids},
        }

    async def _premium_access_expires_at(
        self,
        user_id: int | None,
    ) -> datetime | None:
        if user_id is None:
            return None
        now = datetime.now(timezone.utc)
        return await self.db.scalar(
            select(func.max(Subscription.expires_at))
            .join(User, User.id == Subscription.user_id)
            .where(
                Subscription.user_id == user_id,
                User.is_deleted.is_(False),
                Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                Subscription.starts_at <= now,
                Subscription.expires_at > now,
            )
        )

    async def _download_access_expires_at(
        self,
        user_id: int | None,
    ) -> datetime | None:
        if user_id is None:
            return None

        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Subscription, Plan.name)
            .join(Plan, Plan.id == Subscription.plan_id)
            .join(User, User.id == Subscription.user_id)
            .where(
                Subscription.user_id == user_id,
                User.is_deleted.is_(False),
                Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                Subscription.starts_at <= now,
                Subscription.expires_at > now,
            )
        )
        expirations = [
            download_access_expires_at(
                plan_name=plan_name,
                starts_at=subscription.starts_at,
                subscription_expires_at=subscription.expires_at,
                now=now,
            )
            for subscription, plan_name in result.all()
        ]
        return max(
            (expires_at for expires_at in expirations if expires_at is not None),
            default=None,
        )

    async def _ensure_gallery_preview(self, image: ImageAsset) -> str:
        preview_key = self._preview_object_key(image.id)
        if not await self.storage.object_exists(preview_key):
            await self._generate_gallery_preview(image)
        return preview_key

    async def _generate_gallery_preview(self, image: ImageAsset) -> None:
        source = await self.storage.get_object_bytes(image.object_key)
        try:
            preview = await asyncio.to_thread(
                create_gallery_preview,
                source,
                image.content_type,
                watermark=image.is_premium,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        await self.storage.put_object_bytes(
            self._preview_object_key(image.id),
            preview,
            "image/webp",
        )

    @staticmethod
    def _preview_object_key(image_id: int) -> str:
        return f"gallery-previews/{image_id}.webp"

    async def _get_gallery_image(self, image_id: int) -> ImageAsset:
        image = await self.db.scalar(
            select(ImageAsset).where(
                ImageAsset.id == image_id,
                ImageAsset.is_gallery.is_(True),
            )
        )
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery image not found.",
            )
        return image

    @staticmethod
    def _serialize(image: ImageAsset) -> dict:
        return {
            "id": image.id,
            "filename": image.original_filename,
            "content_type": image.content_type,
            "size_bytes": image.size_bytes,
            "status": image.status,
            "is_premium": image.is_premium,
            "created_at": image.created_at,
        }
