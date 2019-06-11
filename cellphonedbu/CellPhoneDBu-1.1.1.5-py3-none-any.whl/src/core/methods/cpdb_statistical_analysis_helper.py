import numpy as np
import pandas as pd
import sys

from dask.distributed import Client
from scipy.stats import mstats

from cellphonedb.src.core.core_logger import core_logger


def log2tf_winsorizer(meta: pd.DataFrame, counts: pd.DataFrame, log2_transform: bool, threads: int) -> dict:
    """
    Builds a cluster structure and calculates the means values
    """
    cluster_names = meta['cell_type'].drop_duplicates().tolist()

    def mstats_winsorizer(s):
        return mstats.winsorize(s, limits=[0, 0.05])

##########
    # def WinsorizeSampleList(data):
    #     # quantiles = data.quantile([0.95])
    #     # q_05 = quantiles.loc[0.05]
    #     # q_95 = quantiles.loc[0.95]

    #     quantiles = data.quantile([0.25, 0.75])
    #     q_25 = quantiles.loc[0.25]
    #     q_75 = quantiles.loc[0.75]
    #     step = (q_75 - q_25) * 1.5
    #     # return data[(data.values >= q_05) & (data.values <= q_95)]
    #     return data[(data.values >= q_75 + step)]
###########

    # Winsorizer function
    def winsorizer_process(cluster_count, log2_transform):

        winsorized_cluster_count_array = cluster_count.apply(mstats_winsorizer, axis=1)
        
        if log2_transform:
            winsorized_cluster_count_array = winsorized_cluster_count_array[:].apply(
                                                    lambda x: np.log2(x + 1))

        return pd.DataFrame.from_records(winsorized_cluster_count_array, \
                                      index=cluster_count.index, columns=cluster_count.columns)

    chunks = [counts.loc[:, meta[meta['cell_type'] == cluster_name].index] for cluster_name in cluster_names]

    # Concatenating the individual dataframes
    def df_concatenate(dfs):

        return pd.concat(dfs, axis=1)

    # Starting DASK client and submitting parallel processing jobs
    client = Client()
    L = [client.submit(winsorizer_process, future, log2_transform) for future in chunks]
    future = client.submit(df_concatenate, L)
    result = future.result()

    return result


