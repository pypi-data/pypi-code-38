import pandas as pd

from cellphonedb.src.core.exceptions.EmptyResultException import EmptyResultException
from cellphonedb.src.core.methods import cpdb_statistical_analysis_simple_method


def call(meta: pd.DataFrame,
         count: pd.DataFrame,
         threads: int,
         debug_seed: int,
         result_precision: int,
         log2_transform: bool
         ) -> (pd.DataFrame):
    winsorized = \
        cpdb_statistical_analysis_simple_method.call(meta.copy(),
                                                     count.copy(),
                                                     threads,
                                                     debug_seed,
                                                     result_precision,
                                                     log2_transform)

    return winsorized
