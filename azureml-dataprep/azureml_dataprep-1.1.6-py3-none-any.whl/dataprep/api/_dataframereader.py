from .errorhandlers import PandasImportError, NumpyImportError
from ._pandas_helper import have_numpy, have_pandas, have_pyarrow
import io
import json
import math
from typing import List


# 20,000 rows gives a good balance between memory requirement and throughput by requiring that only
# (20000 * CPU_CORES) rows are materialized at once while giving each core a sufficient amount of
# work.
PARTITION_SIZE = 20000


class _InconsistentSchemaError(Exception):
    def __init__(self):
        super().__init__('Inconsistent schemas encountered between partitions.')


class _DataFrameReader:
    def __init__(self):
        self._outgoing_dataframes = {}
        self._incoming_dataframes = {}

    def register_outgoing_dataframe(self, dataframe: 'pandas.DataFrame', dataframe_id: str):
        self._outgoing_dataframes[dataframe_id] = dataframe

    def unregister_outgoing_dataframe(self, dataframe_id: str):
        self._outgoing_dataframes.pop(dataframe_id)

    def _get_partitions(self, dataframe_id: str) -> int:
        dataframe = self._outgoing_dataframes[dataframe_id]
        partition_count = math.ceil(len(dataframe) / PARTITION_SIZE)
        return partition_count

    def _get_data(self, dataframe_id: str, partition: int) -> bytes:
        if not have_numpy():
            raise NumpyImportError()
        else:
            import numpy as np
        if not have_pandas():
            raise PandasImportError()
        else:
            import pandas as pd

        from azureml.dataprep import native
        dataframe = self._outgoing_dataframes[dataframe_id]
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

    def register_incoming_dataframe(self, dataframe_id: str, extended_types: bool, nulls_as_nans: bool):
        self._incoming_dataframes[dataframe_id] = ({}, extended_types, nulls_as_nans)

    def complete_incoming_dataframe(self, dataframe_id: str) -> 'pandas.DataFrame':
        import pyarrow
        partitions_dfs, extended_types, nulls_as_nans = self._incoming_dataframes[dataframe_id]
        partitions_dfs = [partitions_dfs[key] for key in sorted(partitions_dfs.keys())]
        self._incoming_dataframes.pop(dataframe_id)

        import pandas as pd
        if len(partitions_dfs) == 0:
            return pd.DataFrame.empty

        def get_column_names(partition: pyarrow.Table) -> List[str]:
            return [c.name for c in partition.columns]

        def verify_column_names():
            expected_names = get_column_names(partitions_dfs[0])
            expected_count = partitions_dfs[0].num_columns
            for partition in partitions_dfs:
                if partition.num_columns != expected_count:
                    raise _InconsistentSchemaError()
                for (a, b) in zip(expected_names, get_column_names(partition)):
                    if a != b:
                        raise _InconsistentSchemaError()

        def determine_column_type(index: int) -> pyarrow.DataType:
            for partition in partitions_dfs:
                column = partition.column(index)
                if column.type != pyarrow.bool_() or column.null_count != column.length():
                    return column.type
            return pyarrow.bool_()

        def apply_column_types(types: List[pyarrow.DataType]):
            for i in range(0, len(partitions_dfs)):
                partition = partitions_dfs[i]
                for j in range(0, len(types)):
                    column = partition.column(j)
                    if column.type != types[j]:
                        if column.type == pyarrow.bool_():
                            partition = partition.remove_column(j)
                            partition = partition.add_column(j, column.cast(types[j]))
                            partitions_dfs[i] = partition
                        else:
                            raise _InconsistentSchemaError()

        verify_column_names()
        column_types = [determine_column_type(i) for i in range(0, partitions_dfs[0].num_columns)]
        apply_column_types(column_types)

        from pyarrow import feather
        df = pyarrow.feather.concat_tables(partitions_dfs).to_pandas(use_threads=True)
        return df

    def _read_incoming_partition(self, dataframe_id: str, partition: int, partition_bytes: bytes):
        if not have_pyarrow():
            raise ImportError('PyArrow is not installed.')
        else:
            from pyarrow import feather
        partitions_dfs, extended_types, nulls_as_nans = self._incoming_dataframes[dataframe_id]
        df = feather.read_table(io.BytesIO(partition_bytes))
        partitions_dfs[partition] = df


_dataframe_reader = None


def get_dataframe_reader():
    global _dataframe_reader
    if _dataframe_reader is None:
        _dataframe_reader = _DataFrameReader()

    return _dataframe_reader


def ensure_dataframe_reader_handlers(requests_channel):
    requests_channel.register_handler('get_dataframe_partitions', process_get_partitions)
    requests_channel.register_handler('get_dataframe_partition_data', process_get_data)
    requests_channel.register_handler('send_partition', process_send_partition)


def process_get_partitions(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    try:
        partition_count = get_dataframe_reader()._get_partitions(dataframe_id)
        writer.write(json.dumps({'result': 'success', 'partitions': partition_count}))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def process_get_data(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        partition_bytes = get_dataframe_reader()._get_data(dataframe_id, partition)
        byte_count = len(partition_bytes)
        byte_count_bytes = byte_count.to_bytes(4, 'little')
        socket.send(byte_count_bytes)
        socket.send(partition_bytes)
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def process_send_partition(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        writer.write(json.dumps({'result': 'success'}) + '\n')
        writer.flush()
        byte_count = int.from_bytes(socket.recv(8), 'little')
        with socket.makefile('rb') as input:
            partition_bytes = input.read(byte_count)
            get_dataframe_reader()._read_incoming_partition(dataframe_id, partition, partition_bytes)
            writer.write(json.dumps({'result': 'success'}) + '\n')
    except ImportError:
        writer.write(json.dumps({'result': 'error', 'error': 'PyArrowMissing'}))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))
