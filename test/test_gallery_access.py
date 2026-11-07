import unittest
from datetime import datetime, timedelta, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image, ImageChops
from fastapi import HTTPException

from src.gallery.controller.Controller import GalleryController
from src.gallery.services.DownloadAccessService import download_access_expires_at
from src.gallery.services.ImagePreviewService import create_gallery_preview
from src.storage.StorjStorage import StorjStorage


class DownloadAccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)

    def test_silver_download_access_expires_after_one_hour(self) -> None:
        expires_at = download_access_expires_at(
            plan_name="Silver",
            starts_at=self.now - timedelta(minutes=10),
            subscription_expires_at=self.now + timedelta(hours=5),
            now=self.now,
        )

        self.assertEqual(expires_at, self.now + timedelta(minutes=50))

    def test_gold_download_access_expires_after_three_hours(self) -> None:
        expires_at = download_access_expires_at(
            plan_name="GOLD",
            starts_at=self.now,
            subscription_expires_at=self.now + timedelta(hours=8),
            now=self.now,
        )

        self.assertEqual(expires_at, self.now + timedelta(hours=3))

    def test_download_access_does_not_outlive_subscription(self) -> None:
        subscription_expiry = self.now + timedelta(minutes=20)
        expires_at = download_access_expires_at(
            plan_name="Silver",
            starts_at=self.now - timedelta(minutes=10),
            subscription_expires_at=subscription_expiry,
            now=self.now,
        )

        self.assertEqual(expires_at, subscription_expiry)

    def test_download_access_requires_current_silver_or_gold_membership(self) -> None:
        common = {
            "starts_at": self.now,
            "subscription_expires_at": self.now + timedelta(hours=5),
            "now": self.now,
        }

        self.assertIsNone(
            download_access_expires_at(plan_name="Free", **common)
        )
        self.assertIsNone(
            download_access_expires_at(
                plan_name="Gold",
                starts_at=self.now + timedelta(minutes=1),
                subscription_expires_at=common["subscription_expires_at"],
                now=self.now,
            )
        )
        self.assertIsNone(
            download_access_expires_at(
                plan_name="Silver",
                starts_at=self.now - timedelta(hours=2),
                subscription_expires_at=self.now + timedelta(hours=2),
                now=self.now,
            )
        )


class GalleryPreviewTests(unittest.TestCase):
    @staticmethod
    def create_jpeg() -> bytes:
        image = Image.new("RGB", (1600, 800), color=(70, 100, 130))
        output = BytesIO()
        image.save(output, format="JPEG")
        return output.getvalue()

    def test_preview_is_webp_and_reduced_in_size(self) -> None:
        preview = create_gallery_preview(
            self.create_jpeg(),
            "image/jpeg",
            watermark=False,
        )

        with Image.open(BytesIO(preview)) as result:
            self.assertEqual(result.format, "WEBP")
            self.assertEqual(result.size, (960, 480))

    def test_premium_preview_contains_watermark(self) -> None:
        source = self.create_jpeg()
        clean_preview = create_gallery_preview(
            source,
            "image/jpeg",
            watermark=False,
        )
        watermarked_preview = create_gallery_preview(
            source,
            "image/jpeg",
            watermark=True,
        )

        with (
            Image.open(BytesIO(clean_preview)) as clean,
            Image.open(BytesIO(watermarked_preview)) as watermarked,
        ):
            self.assertIsNotNone(ImageChops.difference(clean, watermarked).getbbox())

    def test_rejects_mismatched_image_content_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match"):
            create_gallery_preview(
                self.create_jpeg(),
                "image/png",
                watermark=True,
            )

    def test_rejects_oversized_image_dimensions(self) -> None:
        image = Image.new("RGB", (5001, 5000), color="white")
        output = BytesIO()
        image.save(output, format="JPEG")

        with self.assertRaisesRegex(ValueError, "dimensions are too large"):
            create_gallery_preview(
                output.getvalue(),
                "image/jpeg",
                watermark=True,
            )


class StorjDownloadUrlTests(unittest.IsolatedAsyncioTestCase):
    async def test_high_resolution_download_is_denied_without_eligible_plan(self) -> None:
        db = AsyncMock()
        db.scalar.return_value = SimpleNamespace(
            status="READY",
            is_gallery=True,
        )
        db.execute.return_value = SimpleNamespace(all=lambda: [])
        storage = AsyncMock()
        controller = GalleryController(db=db, storage=storage)

        with self.assertRaises(HTTPException) as raised:
            await controller.create_download(image_id=1, user_id=42)

        self.assertEqual(raised.exception.status_code, 403)
        storage.get_image_url.assert_not_awaited()

    async def test_download_url_is_attachment_and_supports_gold_window(self) -> None:
        storage = StorjStorage()
        client = MagicMock()
        client.generate_presigned_url.return_value = "https://storage.example/download"

        with patch.object(
            storage,
            "_get_client_and_bucket",
            return_value=(client, "gallery"),
        ):
            url = await storage.get_image_url(
                "gallery/full-resolution.jpg",
                expires_in=10800,
                use_public_url=False,
                download_filename="photo name.jpg",
            )

        self.assertEqual(url, "https://storage.example/download")
        client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={
                "Bucket": "gallery",
                "Key": "gallery/full-resolution.jpg",
                "ResponseContentDisposition": (
                    "attachment; filename*=UTF-8''photo%20name.jpg"
                ),
            },
            ExpiresIn=10800,
        )


if __name__ == "__main__":
    unittest.main()
