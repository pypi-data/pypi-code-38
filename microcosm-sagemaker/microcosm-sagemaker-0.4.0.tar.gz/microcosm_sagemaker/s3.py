from dataclasses import dataclass
from urllib.parse import urlparse

from boto3 import client
from botocore.exceptions import ClientError


@dataclass
class S3Object:
    bucket: str
    key: str

    @property
    def path(self) -> str:
        return f"s3://{self.bucket}/{self.key}"

    @property
    def exists(self) -> bool:
        try:
            s3 = client("s3")
            s3.head_object(Bucket=self.bucket, Key=self.key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise
        else:
            return True

    @classmethod
    def from_url(cls, url):
        parsed = urlparse(url)
        return cls(bucket=parsed.netloc, key=parsed.path.strip("/"))
