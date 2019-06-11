import pandas as pd

from cellphonedb.src.core.core_logger import core_logger
from cellphonedb.src.core.exceptions.ThresholdValueException import ThresholdValueException
from cellphonedb.src.core.methods import cpdb_statistical_analysis_method
from cellphonedb.src.core.preprocessors import method_preprocessors
from cellphonedb.src.exceptions.ParseCountsException import ParseCountsException


class MethodLauncher():
    def __init__(self, default_threads: int):
        self.default_threads = default_threads

    def __getattribute__(self, name):
        method = object.__getattribute__(self, name)
        if hasattr(method, '__call__'):
            core_logger.info('Launching Method {}'.format(name))

        return method

    def cpdb_statistical_analysis_launcher(self,
                                           raw_meta: pd.DataFrame,
                                           counts: pd.DataFrame,
                                           threads: int,
                                           debug_seed: int,
                                           result_precision: int,
                                           log2_transform: bool
                                           ) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):

        if threads < 1:
            core_logger.info('Using Default thread number: %s' % self.default_threads)
            threads = self.default_threads


        meta = method_preprocessors.meta_preprocessor(raw_meta)
        counts = self._counts_validations(counts, meta)

        winsorized = \
            cpdb_statistical_analysis_method.call(meta,
                                                  counts,
                                                  threads,
                                                  debug_seed,
                                                  result_precision,
                                                  log2_transform)

        return winsorized


    def _counts_validations(self, counts: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
        if not len(counts.columns):
            raise ParseCountsException('Counts values are not decimal values', 'Incorrect file format')
        try:
            counts = counts.astype(pd.np.float)  # type: pd.DataFrame
        except:
            raise ParseCountsException
        for cell in meta.index.values:
            if cell not in counts.columns.values:
                raise ParseCountsException('Some cells in meta didnt exist in counts columns',
                                           'Maybe incorrect file format')
        return counts
