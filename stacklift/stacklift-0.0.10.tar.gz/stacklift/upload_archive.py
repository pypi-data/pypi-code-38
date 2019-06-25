import boto3
from urllib.parse import urlparse


def upload_archive(archive_url, archive_path):
    url = urlparse(archive_url)
    if url.scheme != "s3":
        raise RuntimeError("Now upload_archive can only upload to s3")

    s3 = boto3.client('s3')
    with open(archive_path, "rb") as fp:
        s3.put_object(Bucket=url.netloc, Key=url.path.lstrip("/"), Body=fp)
