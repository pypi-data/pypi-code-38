from stacklift.global_config import GlobalConfig
import boto3
from urllib.parse import urlparse
import tempfile
import shutil
import os


def extract_archive_file(path, target_dir):
    shutil.unpack_archive(path, target_dir)


def extract_archive_s3(bucket, key, target_dir):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    with tempfile.NamedTemporaryFile(suffix=os.path.basename(key)) as temp:
        shutil.copyfileobj(response["Body"], temp)
        temp.flush()
        shutil.unpack_archive(temp.name, target_dir)


def extract_archive(config_file):
    config_dir = os.path.dirname(config_file)

    global_config = GlobalConfig(config_file)
    module_dir = global_config.get_module_dir()
    archive_location = global_config.get_archive_location()

    if archive_location.startswith("s3://"):
        url = urlparse(archive_location)
        extract_archive_s3(url.netloc, url.path.lstrip('/'), module_dir)
    else:
        extract_archive_file(os.path.join(config_dir, archive_location), module_dir)
