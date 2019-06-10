from .engineapi.enginerequests import get_requests_channel
from .errorhandlers import PandasImportError, NumpyImportError
from ._pandas_helper import have_numpy, have_pandas
import json
import math


# 20,000 rows gives a good balance between memory requirement and throughput by requiring that only
# (20000 * CPU_CORES) rows are materialized at once while giving each core a sufficient amount of
# work.
PARTITION_SIZE = 20000


class _DataFrameReader:
    def __init__(self):
        self._registered_dataframes = {}

    def register_dataframe(self, dataframe: 'pandas.DataFrame', dataframe_id: str):
        self._registered_dataframes[dataframe_id] = dataframe

    def unregister_dataframe(self, dataframe_id: str):
        self._registered_dataframes.pop(dataframe_id)

    def get_partitions(self, dataframe_id: str) -> int:
        dataframe = self._registered_dataframes[dataframe_id]
        partition_count = math.ceil(len(dataframe) / PARTITION_SIZE)
        return partition_count

    def get_data(self, dataframe_id: str, partition: int) -> bytes:
        if not have_numpy():
            raise NumpyImportError()
        else:
            import numpy as np
        if not have_pandas():
            raise PandasImportError()
        else:
            import pandas as pd
        from azureml.dataprep import native
        dataframe = self._registered_dataframes[dataframe_id]
        start = partition * PARTITION_SIZE
        end = min(len(dataframe), start + PARTITION_SIZE)
        dataframe = dataframe.iloc[start:end]

        new_schema = dataframe.columns.tolist()
        new_values = []
        # Handle Categorical typed columns. Categorical is a pandas type not a numpy type and azureml-dataprep-native
        # can't handle it. This is temporary pending improvements to native that can handle Categoricals, vso: 246011
        for column_name in new_schema:
            if pd.api.types.is_categorical_dtype(dataframe[column_name]):
                new_values.append(np.asarray(dataframe[column_name]))
            else:
                new_values.append(dataframe[column_name].values)

        return native.preppy_from_ndarrays(new_values, new_schema)


_dataframe_reader = None


def get_dataframe_reader():
    global _dataframe_reader
    if _dataframe_reader is None:
        _dataframe_reader = _DataFrameReader()
        get_requests_channel().register_handler('get_dataframe_partitions', process_get_partitions)
        get_requests_channel().register_handler('get_dataframe_partition_data', process_get_data)

    return _dataframe_reader


def process_get_partitions(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    try:
        partition_count = get_dataframe_reader().get_partitions(dataframe_id)
        writer.write(json.dumps({'result': 'success', 'partitions': partition_count}))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def process_get_data(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        partition_bytes = get_dataframe_reader().get_data(dataframe_id, partition)
        byte_count = len(partition_bytes)
        byte_count_bytes = byte_count.to_bytes(4, 'little')
        socket.send(byte_count_bytes)
        socket.send(partition_bytes)
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))
