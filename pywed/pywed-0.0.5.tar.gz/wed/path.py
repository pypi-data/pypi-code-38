import os
import datetime
from wed.utils import DataType, Service
from wed import settings


class DatasetPath:
    """
    Describe the location of a Dataset.
    A dataset is a set of one file per day
    """
    def __init__(self, bucket: str, local_cache_path: str,
                 type: DataType, service: Service):
        self.bucket = bucket
        self.local_cache_path = local_cache_path
        self.type = type
        self.service = service

    @property
    def prefix(self):
        return settings.get_prefix(self.type, self.service)

    @property
    def local_path(self):
        return os.path.join(self.local_cache_path, self.prefix)


class DatafilePath:
    """
    Describe the location of a Datafile.
    A datafile is a single file either remote or locally hosted
    """
    def __init__(self, dataset_path: DatasetPath, time: datetime.datetime):
        self.path = dataset_path
        self.__filename = time.isoformat().split('T')[0] + ".grb"

    @property
    def local_path(self):
        return os.path.join(self.path.local_path, self.__filename)

    @property
    def bucket(self):
        return self.path.bucket

    @property
    def prefix(self):
        return os.path.join(self.path.prefix, self.__filename)
