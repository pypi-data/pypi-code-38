import os
import datetime
import functools
import logging
import time

from typing import List

import cfgrib
import xarray
import numpy as np

from wed import settings
from wed.path import DatasetPath, DatafilePath
from wed.utils import Coordinate, DataType, Service, round_to_precision
from wed.network import download


class Database:
    def __init__(self,
                 data_types: List[DataType],
                 date_start: datetime.datetime,
                 date_end=None,
                 cache_duration=datetime.timedelta(days=30)):
        self.__date_start = date_start
        self.__date_end = self.__date_start + cache_duration
        if date_end is not None:
            self.__date_end = date_end
        self.__data_types = []

        # load data in memory
        self.__data = {}

        # This is parallelizable
        for data_type in data_types:  # for each data type
            data = {}
            date = self.__date_start.date()
            while date <= self.__date_end.date():
                # Find the dataset
                dataset_path = DatasetPath(
                    settings.Settings().bucket,
                    settings.Settings().local_cache_path,
                    data_type,
                    settings.Settings().services[data_type]
                )
                file_path = DatafilePath(dataset_path, date)
                # Download if needed
                if not os.path.exists(file_path.local_path):
                    logging.info("Datafile at " + file_path.local_path + " not found. Downloading...")
                    download(file_path)
                    logging.info("Download successful")
                # load in memory !
                dataset = cfgrib.open_dataset(file_path.local_path)
                dataset.load()
                data[date] = dataset
                # move to next date !
                date += datetime.timedelta(days=1)  # We download per day

            # add the data for this data type in the cache
            self.__data[data_type] = data

    def read(self, type: DataType, time: datetime.datetime, coordinate: Coordinate):
        dataset = self.__data[type][time.date()]
        # TODO: use and interpolation ?
        value = dataset.sel(
            time=np.datetime64(time),
            longitude=coordinate.longitude,
            latitude=coordinate.latitude,
            method='nearest'
        )
        retval = {}
        for var in value.data_vars:
            retval[var] = float(value[var].values)
        return retval


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

    # value = dataset.interp({
    #     'latitude': latitude,
    #     'longitude': longitude,
    #     'time': np.datetime64(time)
    # }, method='linear')
    value = dataset.sel(
        time=np.datetime64(time),
        longitude=longitude,
        latitude=latitude,
        method='nearest'
    )

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
