"""S3 storage utilities."""

import json
from typing import Any, BinaryIO
import boto3
from botocore.exceptions import ClientError

from ..config import settings
from .logger import setup_logger

logger = setup_logger(__name__)


class S3Storage:
    """S3 storage service for audio files and transcripts."""

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    async def upload_file(
        self,
        file_obj: BinaryIO,
        bucket: str,
        key: str,
        content_type: str = None
    ) -> str:
        """
        Upload a file to S3.

        Args:
            file_obj: File object to upload
            bucket: S3 bucket name
            key: S3 object key
            content_type: Content type of the file

        Returns:
            URL of the uploaded file
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs=extra_args
            )

            # Generate URL
            url = f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
            logger.info(f"Uploaded file to S3: {url}")

            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise

    async def upload_json(
        self,
        data: dict,
        bucket: str,
        key: str
    ) -> str:
        """
        Upload JSON data to S3.

        Args:
            data: Dictionary to upload as JSON
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            URL of the uploaded file
        """
        try:
            json_str = json.dumps(data, indent=2)

            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json_str.encode('utf-8'),
                ContentType='application/json'
            )

            url = f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
            logger.info(f"Uploaded JSON to S3: {url}")

            return url

        except ClientError as e:
            logger.error(f"Error uploading JSON to S3: {e}")
            raise

    async def download_file(
        self,
        bucket: str,
        key: str,
        local_path: str
    ) -> str:
        """
        Download a file from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Local file path to save to

        Returns:
            Local file path
        """
        try:
            self.s3_client.download_file(bucket, key, local_path)
            logger.info(f"Downloaded file from S3: {key} -> {local_path}")
            return local_path

        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise

    async def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for temporary access to an S3 object.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
