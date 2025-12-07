from pydantic import BaseModel

from src.core.config import settings


class AWSConfig(BaseModel):
    region: str = settings.AWS_REGION
    access_key_id: str | None = settings.AWS_ACCESS_KEY_ID
    secret_access_key: str | None = settings.AWS_SECRET_ACCESS_KEY


class SESConfig(AWSConfig):
    from_email: str = settings.SES_FROM_EMAIL
    from_name: str = settings.SES_FROM_NAME


class S3Config(AWSConfig):
    bucket_name: str = settings.S3_BUCKET_NAME
    presigned_url_expiry: int = settings.S3_PRESIGNED_URL_EXPIRY


aws_config = AWSConfig()
ses_config = SESConfig()
s3_config = S3Config()
