import os
import datetime
import functools
import logging

import cfgrib
import numpy as np

from wed import settings
from wed.path import DatasetPath, DatafilePath
from wed.utils import Coordinate, DataType
from wed.network import download


class Database:
    def __init__(self):
        self.bucket = settings.DEFAULT_BUCKET
        self.original_services = settings.DEFAULT_SERVICES
        self.local_cache_path = settings.DEFAULT_CACHE_PATH

    def open_dataset(self, type: DataType):
        service = self.original_services[type]
        path = DatasetPath(
            self.bucket, self.local_cache_path, type, service)
        return Dataset(path)


# Use the LRU cache property to avoid reopenning the dataset each time
@functools.lru_cache(maxsize=10)
def get_dataset(path: str):
    return cfgrib.open_dataset(path)

class Dataset:
    def __init__(self, path: DatasetPath):
        self.path = path

    def read(self, time: datetime.datetime, coordinate: Coordinate):
        # Make sure we are in the time range
        time_range = settings.get_time_range(self.path.type, self.path.service)
        if time_range['max'] < time or time_range['min'] > time:
            raise Exception("Time out of bounds")

        fp = DatafilePath(self.path, time)
        if not os.path.exists(fp.local_path):
            logging.info("Datafile at " + fp.local_path + " not found. Downloading...")
            download(fp)
            logging.info("Download successful")

        dataset = get_dataset(fp.local_path)  # get from cache or create

        # get the coordinates considering the latitude range
        longitude = coordinate.longitude
        while longitude < dataset.longitude[0].data:
            longitude += 360
        while longitude > dataset.longitude[-1].data:
            longitude -= 360

        # read the right value by interpolating it
        value = dataset.interp({
            'latitude': coordinate.latitude,
            'longitude': longitude,
            'time': np.datetime64(time)
        }, method='linear')

        # cast the xarray dataset to a dict
        retval = {}
        for var in value.data_vars:
            retval[var] = float(value[var].values)
        return retval
