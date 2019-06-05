import os
import datetime
import functools
import logging

import cfgrib
import xarray
import numpy as np

from wed import settings
from wed.path import DatasetPath, DatafilePath
from wed.utils import Coordinate, DataType, Service, round_to_precision
from wed.network import download


## ---- Cached functions is used to speed up accesses
# Use the LRU cache property to avoid reopenning the dataset each time
@functools.lru_cache(maxsize=100)
def get_dataset(bucket:str,
                service: Service,
                local_cache_path: str,
                type: DataType,
                timestamp: float) -> xarray.Dataset:
    time = datetime.datetime.fromtimestamp(timestamp)
    dataset_path = DatasetPath(bucket, local_cache_path, type, service)
    file_path = DatafilePath(dataset_path, time)
    if not os.path.exists(file_path.local_path):
        logging.info("Datafile at " + file_path.local_path + " not found. Downloading...")
        download(file_path)
        logging.info("Download successful")
    return cfgrib.open_dataset(file_path.local_path)

# To use the lru_cache effectively we need to keep it to simple types (no datetime of coordinate)
@functools.lru_cache(maxsize=10000)
def get_data(bucket:str,               # The s3 bucket where the database can be found
             service: Service,         # The service to be used
             local_cache_path: str,    # The place were datafiles were downloaded
             type: DataType,           # The type of data to download (wind / wave ...)
             timestamp: float,         # The date of the desired data as timestamp
             latitude: float,
             longitude: float) -> dict:
    time = datetime.datetime.fromtimestamp(timestamp)
    dataset = get_dataset(bucket, service, local_cache_path, type, timestamp)
    value = dataset.interp({
        'latitude': latitude,
        'longitude': longitude,
        'time': np.datetime64(time)
    }, method='linear')

    retval = {}
    for var in value.data_vars:
        retval[var] = float(value[var].values)
    return retval

def read(type: DataType, time: datetime.datetime, coordinate: Coordinate) -> dict:
    # Round the time
    timestamp = time.timestamp()
    time_precision = settings.Settings().time_precision
    if time_precision is not None:
        timestamp = round_to_precision(timestamp, time_precision.total_seconds())

    return get_data(settings.Settings().bucket,
                    settings.Settings().services[type],
                    settings.Settings().local_cache_path,
                    type,
                    timestamp,
                    round_to_precision(coordinate.latitude, settings.Settings().latitude_precision),
                    round_to_precision(coordinate.longitude, settings.Settings().longitude_precision))
