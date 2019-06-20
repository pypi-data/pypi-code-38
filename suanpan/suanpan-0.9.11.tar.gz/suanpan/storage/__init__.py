# coding=utf-8
from __future__ import absolute_import, print_function

import itertools
import tempfile

from suanpan.arguments import Bool, Int, String
from suanpan.proxy import Proxy
from suanpan.storage.local import LocalStorage
from suanpan.storage.minio import MinioStorage
from suanpan.storage.oss import OssStorage

DEFAULT_TEMP_STORE = tempfile.gettempdir()


class StorageProxy(Proxy):
    MAPPING = {"oss": OssStorage, "local": LocalStorage, "minio": MinioStorage}
    DEFAULT_ARGUMENTS = [String("storage-type")]
    OSS_ARGUMENTS = [
        String("storage-oss-access-id"),
        String("storage-oss-access-key"),
        String("storage-oss-bucket-name", default="suanpan"),
        String("storage-oss-endpoint", default="http://oss-cn-beijing.aliyuncs.com"),
        String("storage-oss-delimiter", default="/"),
        String("storage-oss-temp-store", default=DEFAULT_TEMP_STORE),
        Int("storage-oss-download-num-threads", default=1),
        String("storage-oss-download-store-name", default=".py-oss-download"),
        Int("storage-oss-upload-num-threads", default=1),
        String("storage-oss-upload-store-name", default=".py-oss-upload"),
    ]
    LOCAL_ARGUMENTS = [String("storage-local-temp-store", default=DEFAULT_TEMP_STORE)]
    MINIO_ARGUMENTS = [
        String("storage-minio-access-key"),
        String("storage-minio-secret-key"),
        String("storage-minio-bucket-name", default="suanpan"),
        String("storage-minio-endpoint"),
        Bool("storage-minio-secure", default=True),
        String("storage-minio-delimiter", default="/"),
        String("storage-minio-temp-store", default=DEFAULT_TEMP_STORE),
    ]
    ARGUMENTS = list(
        itertools.chain(
            DEFAULT_ARGUMENTS, OSS_ARGUMENTS, LOCAL_ARGUMENTS, MINIO_ARGUMENTS
        )
    )


storage = StorageProxy()
