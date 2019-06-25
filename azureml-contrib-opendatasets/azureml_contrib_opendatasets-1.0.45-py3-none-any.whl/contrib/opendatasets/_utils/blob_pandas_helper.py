# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.storage.blob import BlockBlobService
import pyarrow.parquet as pq
import pandas as pd
from io import BytesIO
from typing import Optional, List


def read_parquet_files(
        target_paths: list,
        blob_container_name: str,
        blob_service: BlockBlobService,
        cols: Optional[List[str]] = None) -> pd.DataFrame:
    '''
    Read parquet files from a list of blob paths, optionally with column name filtered.

    :param target_paths: relative paths to blob container.
    :type target_paths: list
    :param blob_container_name: blob container name.
    :type blob_container_name: str
    :param blob_service: block blob service object.
    :type blob_service: BlockBlobService
    :param cols: a list of column names. If None, then read all columns.
    :type cols: Optional[List[str]]

    :return: concatenated Pandas dataframe.
    :rtype: pandas.DataFrame
    '''
    pandas_dfs = []
    print('Reading them into Pandas dataframe...')
    for path in target_paths:
        byte_stream = BytesIO()
        print('Reading %s under container %s' % (path, blob_container_name))
        try:
            blob_service.get_blob_to_stream(container_name=blob_container_name, blob_name=path, stream=byte_stream)
            df = pq.read_table(source=byte_stream, columns=cols).to_pandas()
            pandas_dfs.append(df)
        finally:
            # Add finally block to ensure closure of the stream
            byte_stream.close()
    if len(pandas_dfs) == 0:
        return None
    all_dfs = pd.concat(pandas_dfs)
    return all_dfs
