"""aws_s3_local_gateway package initialization."""
from .storage import LocalS3Gateway, S3Object

__all__ = ["LocalS3Gateway", "S3Object"]
