import os
import pandas as pd

from cellphonedb.src.app.app_logger import app_logger
from cellphonedb.src.app.cellphonedb_app import output_dir
from cellphonedb.src.exceptions.ParseCountsException import ParseCountsException
from cellphonedb.src.exceptions.ParseMetaException import ParseMetaException
from cellphonedb.utils import utils


class LocalMethodLauncher(object):
    def __init__(self, cellphonedb_app):

        self.cellphonedb_app = cellphonedb_app

    def __getattribute__(self, name):
        method = object.__getattribute__(self, name)
        if hasattr(method, '__call__'):
            app_logger.info('Launching Method {}'.format(name))

        return method

    def cpdb_statistical_analysis_local_method_launcher(self, meta_filename: str,
                                                        counts_filename: str,
                                                        project_name: str = '',
                                                        output_path: str = '',
                                                        winsorized_result_name: str = 'winsorized_count.txt',
                                                        debug_seed: int = -1,
                                                        threads: int = -1,
                                                        result_precision: int = 3,
                                                        log2_transform: bool = True) -> None:
        output_path = self._set_paths(output_path, project_name)

        debug_seed = int(debug_seed)
        threads = int(threads)
        result_precision = int(result_precision)

        counts, meta = self._load_meta_counts(counts_filename, meta_filename)

        winsorized = \
            self.cellphonedb_app.method.cpdb_statistical_analysis_launcher(
                meta,
                counts,
                threads,
                debug_seed,
                result_precision,
                log2_transform)

        winsorized.to_csv('{}/{}'.format(output_path, winsorized_result_name), sep='\t', index=True)
            

    @staticmethod
    def _path_is_empty(path):
        return bool([f for f in os.listdir(path) if not f.startswith('.')])

    @staticmethod
    def _set_paths(output_path, project_name):
        if not output_path:
            output_path = output_dir
        if project_name:
            output_path = os.path.realpath(os.path.expanduser('{}/{}'.format(output_path, project_name)))
        os.makedirs(output_path, exist_ok=True)
        if LocalMethodLauncher._path_is_empty(output_path):
            app_logger.warning(
                'Output directory ({}) exist and is not empty. Result can overwrite old results'.format(output_path))
        return output_path

    @staticmethod
    def _load_meta_counts(counts_filename: str, meta_filename: str) -> (pd.DataFrame, pd.DataFrame):
        """
        :raise ParseMetaException
        """
        meta = utils.read_data_table_from_file(os.path.realpath(meta_filename))
        counts = utils.read_data_table_from_file(os.path.realpath(counts_filename), index_column_first=True)

        return counts, meta
