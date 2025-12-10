import asyncio
import logging
import mimetypes
from typing import Any, cast
from uuid import UUID

import boto3
from botocore.exceptions import ClientError

from src.aws.config import s3_config
from src.aws.exceptions import FileDeleteError, FileUploadError
from src.aws.utils import retry
from src.core.config import settings
from src.core.models import generate_uuid7


logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self) -> None:
        self._client: Any | None = None

    def _guess_content_type(self, filename: str) -> str:
        """Guess the MIME type of a file based on its filename."""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def _is_dev_mode_without_credentials(self) -> bool:
        """Check if running in development mode without AWS credentials."""
        return settings.is_development and not s3_config.access_key_id

    def _build_s3_url(self, key: str) -> str:
        """Build the S3 URL for a given key."""
        return f"https://{s3_config.bucket_name}.s3.amazonaws.com/{key}"

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=s3_config.region,
                aws_access_key_id=s3_config.access_key_id,
                aws_secret_access_key=s3_config.secret_access_key,
            )
        return self._client

    def _generate_key(
        self,
        folder: str,
        filename: str,
        community_id: UUID | None = None,
    ) -> str:
        file_uuid = generate_uuid7()
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        safe_extension = f".{extension}" if extension else ""

        if community_id:
            return f"communities/{community_id}/{folder}/{file_uuid}{safe_extension}"
        return f"{folder}/{file_uuid}{safe_extension}"

    @retry
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "uploads",
        community_id: UUID | None = None,
        content_type: str | None = None,
    ) -> str:
        # Input validation
        if not file_content:
            raise ValueError("File content cannot be empty")
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty or whitespace-only")

        key = self._generate_key(folder, filename, community_id)
        content_type = content_type or self._guess_content_type(filename)

        if self._is_dev_mode_without_credentials():
            logger.info(f"[DEV] Would upload file to S3: {key}")
            return self._build_s3_url(key)

        try:
            # Use asyncio.to_thread to run the blocking put_object in a thread pool
            await asyncio.to_thread(
                self.client.put_object,
                Bucket=s3_config.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type,
            )
            logger.info(f"File uploaded successfully: {key}")
            return self._build_s3_url(key)

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchBucket":
                logger.error(f"Bucket does not exist: {s3_config.bucket_name}")
                raise FileUploadError(
                    f"S3 bucket '{s3_config.bucket_name}' does not exist"
                ) from e
            elif error_code == "AccessDenied":
                logger.error(f"Access denied for bucket: {s3_config.bucket_name}")
                raise FileUploadError("Access denied to S3 bucket") from e
            elif error_code == "InvalidBucketName":
                logger.error(f"Invalid bucket name: {s3_config.bucket_name}")
                raise FileUploadError("Invalid S3 bucket name") from e
            else:
                logger.error(f"Failed to upload file {key}: {error_code} - {e}")
                raise FileUploadError(f"S3 upload failed: {error_code}") from e

    @retry
    async def delete_file(self, file_url: str) -> bool:
        key = file_url.replace(f"https://{s3_config.bucket_name}.s3.amazonaws.com/", "")

        if settings.is_development and not s3_config.access_key_id:
            logger.info(f"[DEV] Would delete file from S3: {key}")
            return True

        try:
            self.client.delete_object(
                Bucket=s3_config.bucket_name,
                Key=key,
            )
            logger.info(f"File deleted successfully: {key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file {key}: {e}")
            raise FileDeleteError(str(e)) from e

    async def generate_presigned_url(
        self,
        file_url: str,
        expiry: int | None = None,
    ) -> str:
        key = file_url.replace(f"https://{s3_config.bucket_name}.s3.amazonaws.com/", "")

        if expiry is None:
            expiry = s3_config.presigned_url_expiry

        if settings.is_development and not s3_config.access_key_id:
            logger.info(f"[DEV] Would generate presigned URL for: {key}")
            return file_url

        try:
            url = cast(
                str,
                self.client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": s3_config.bucket_name,
                        "Key": key,
                    },
                    ExpiresIn=expiry,
                ),
            )
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {key}: {e}")
            return file_url

    async def generate_presigned_upload_url(
        self,
        filename: str,
        folder: str = "uploads",
        community_id: UUID | None = None,
        content_type: str | None = None,
        expiry: int | None = None,
    ) -> dict[str, str]:
        key = self._generate_key(folder, filename, community_id)

        if content_type is None:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        if expiry is None:
            expiry = s3_config.presigned_url_expiry

        if settings.is_development and not s3_config.access_key_id:
            logger.info(f"[DEV] Would generate presigned upload URL for: {key}")
            return {
                "upload_url": f"https://{s3_config.bucket_name}.s3.amazonaws.com/{key}",
                "file_url": f"https://{s3_config.bucket_name}.s3.amazonaws.com/{key}",
                "key": key,
            }

        try:
            upload_url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": s3_config.bucket_name,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expiry,
            )
            return {
                "upload_url": upload_url,
                "file_url": f"https://{s3_config.bucket_name}.s3.amazonaws.com/{key}",
                "key": key,
            }

        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise FileUploadError(str(e)) from e


s3_service = S3Service()
