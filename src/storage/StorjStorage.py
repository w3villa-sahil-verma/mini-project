import asyncio
from urllib.parse import quote, urlsplit

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from src.core.settings import settings


class StorjStorage:
    def __init__(self) -> None:
        self._endpoint = settings.STORJ_S3_ENDPOINT
        self._access_key = settings.STORJ_ACCESS_KEY
        self._secret_key = settings.STORJ_SECRET_KEY
        self._bucket = settings.STORJ_BUCKET
        self._region = settings.STORJ_REGION
        self._public_base_url = settings.STORJ_PUBLIC_BASE_URL.rstrip("/")

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

    async def object_exists(self, object_key: str) -> bool:
        client, bucket = self._get_client_and_bucket()
        try:
            await asyncio.to_thread(
                client.head_object,
                Bucket=bucket,
                Key=object_key,
            )
            return True
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not check the stored image.",
            ) from error
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not check the stored image.",
            ) from error

    async def get_object_bytes(self, object_key: str) -> bytes:
        client, bucket = self._get_client_and_bucket()

        def read_object() -> bytes:
            response = client.get_object(Bucket=bucket, Key=object_key)
            body = response["Body"]
            try:
                return body.read()
            finally:
                body.close()

        try:
            return await asyncio.to_thread(read_object)
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Stored image not found.",
                ) from error
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not read the stored image.",
            ) from error
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not read the stored image.",
            ) from error

    async def put_object_bytes(
        self,
        object_key: str,
        content: bytes,
        content_type: str,
    ) -> None:
        client, bucket = self._get_client_and_bucket()
        try:
            await asyncio.to_thread(
                client.put_object,
                Bucket=bucket,
                Key=object_key,
                Body=content,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError) as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not save the image preview.",
            ) from error

    async def delete_object(self, object_key: str) -> None:
        client, bucket = self._get_client_and_bucket()
        try:
            await asyncio.to_thread(
                client.delete_object,
                Bucket=bucket,
                Key=object_key,
            )
        except (BotoCoreError, ClientError) as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not delete the image from storage.",
            ) from error

    async def get_image_url(
        self,
        object_key: str,
        *,
        expires_in: int = 3600,
        use_public_url: bool = True,
        download_filename: str | None = None,
    ) -> str:
        public_url = self.public_url(object_key) if use_public_url else None
        if public_url:
            return public_url

        client, bucket = self._get_client_and_bucket()
        if expires_in < 1 or expires_in > 10800:
            raise ValueError("Signed image URL lifetime must be between 1 and 10800 seconds.")
        params = {"Bucket": bucket, "Key": object_key}
        if download_filename is not None:
            params["ResponseContentDisposition"] = (
                f"attachment; filename*=UTF-8''{quote(download_filename, safe='')}"
            )
        try:
            return await asyncio.to_thread(
                client.generate_presigned_url,
                "get_object",
                Params=params,
                ExpiresIn=expires_in,
            )
        except BotoCoreError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not create an image URL.",
            ) from error

    def public_url(self, object_key: str) -> str | None:
        base_url = self._public_base_url
        if not base_url:
            return None
        bucket = self._bucket
        if not bucket:
            return None
        path_segments = [
            segment
            for segment in urlsplit(base_url).path.strip("/").split("/")
            if segment
        ]
        if path_segments == ["raw"]:
            return None
        return (
            f"{base_url}/{quote(bucket, safe='')}"
            f"/{quote(object_key, safe='/')}"
        )

    def _get_client_and_bucket(self) -> tuple[BaseClient, str]:
        if not all(
            (self._endpoint, self._access_key, self._secret_key, self._bucket)
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Image storage is not configured.",
            )

        client = boto3.client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
        )
        return client, self._bucket
