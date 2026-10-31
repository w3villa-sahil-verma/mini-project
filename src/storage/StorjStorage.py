import asyncio
import os
from pathlib import Path
from urllib.parse import quote

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status


class StorjStorage:
    def __init__(self) -> None:
        self._settings = self._load_settings()

    async def create_upload_url(self, object_key: str, content_type: str) -> str:
        client, bucket = self._get_client_and_bucket()
        try:
            return await asyncio.to_thread(
                client.generate_presigned_url,
                "put_object",
                Params={
                    "Bucket": bucket,
                    "Key": object_key,
                    "ContentType": content_type,
                },
                ExpiresIn=60,
            )
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not create an upload URL for image storage.",
            ) from error

    async def verify_upload(
        self,
        object_key: str,
        expected_content_type: str,
        expected_size: int,
    ) -> None:
        client, bucket = self._get_client_and_bucket()
        try:
            metadata = await asyncio.to_thread(
                client.head_object,
                Bucket=bucket,
                Key=object_key,
            )
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The image has not been uploaded to storage.",
                ) from error
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not verify the uploaded image.",
            ) from error
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not verify the uploaded image.",
            ) from error

        if (
            metadata.get("ContentType") != expected_content_type
            or metadata.get("ContentLength") != expected_size
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded image metadata does not match the requested file.",
            )

    async def get_image_url(self, object_key: str, public_url: str | None) -> str:
        if public_url:
            return public_url

        client, bucket = self._get_client_and_bucket()
        try:
            return await asyncio.to_thread(
                client.generate_presigned_url,
                "get_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=3600,
            )
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not create an image URL.",
            ) from error

    def public_url(self, object_key: str) -> str | None:
        base_url = self._settings["public_base_url"]
        if not base_url:
            return None
        return f"{base_url}/{quote(object_key, safe='/')}"

    def _get_client_and_bucket(self) -> tuple[BaseClient, str]:
        endpoint = self._settings["endpoint"]
        access_key = self._settings["access_key"]
        secret_key = self._settings["secret_key"]
        bucket = self._settings["bucket"]
        region = self._settings["region"]

        if not all((endpoint, access_key, secret_key, bucket)):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Image storage is not configured.",
            )

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        return client, bucket

    @staticmethod
    def _load_settings() -> dict[str, str]:
        settings = {
            "endpoint": os.getenv("STORJ_S3_ENDPOINT", ""),
            "access_key": os.getenv("STORJ_ACCESS_KEY", ""),
            "secret_key": os.getenv("STORJ_SECRET_KEY", ""),
            "bucket": os.getenv("STORJ_BUCKET", ""),
            "region": os.getenv("STORJ_REGION", "us-east-1"),
            "public_base_url": os.getenv("STORJ_PUBLIC_BASE_URL", "").rstrip("/"),
        }

        env_file = Path(__file__).resolve().parents[1] / ".env"
        if env_file.is_file():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                key, separator, value = line.partition("=")
                if not separator:
                    continue
                normalized_key = key.strip()
                setting_name = {
                    "STORJ_S3_ENDPOINT": "endpoint",
                    "STORJ_ACCESS_KEY": "access_key",
                    "STORJ_SECRET_KEY": "secret_key",
                    "STORJ_BUCKET": "bucket",
                    "STORJ_REGION": "region",
                    "STORJ_PUBLIC_BASE_URL": "public_base_url",
                }.get(normalized_key)
                if setting_name and not settings[setting_name]:
                    settings[setting_name] = value.strip().strip("\"'")

        settings["public_base_url"] = settings["public_base_url"].rstrip("/")
        return settings
