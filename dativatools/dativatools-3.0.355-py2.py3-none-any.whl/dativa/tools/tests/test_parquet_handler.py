import logging
import unittest
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from dativa.tools.pandas import ParquetHandler


logger = logging.getLogger("dativa.parquet_handler.tests")


class ParquetTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("Running setup class")
        self.orig_base_path = "{0}/test_data/parquet".format(os.path.dirname(os.path.abspath(__file__)))
        self.parquet_basic = os.path.join(self.orig_base_path, 'data.parquet')

    def _get_parquet_handler(self):
        pq_obj = ParquetHandler()
        return pq_obj

    def _get_parquet_file_row_group(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler(parquet_file_path, 0)
        return pq_obj

    def _get_parquet_file_multiple_row_groups(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_row_groups.parquet')
        pq_obj = ParquetHandler(parquet_file_path, 1)
        return pq_obj

    def _get_parquet_file_compression(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_gzip.parquet')
        pq_obj = ParquetHandler(parquet_file_path)
        return pq_obj

    def test_load_df(self):
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(self.parquet_basic)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_row_groups(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_row_groups.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_cols(self):
        pq_obj = ParquetHandler()
        cols_names = ['registration_dttm', 'id',
                      'first_name', 'last_name', 'gender']
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        df = pq_obj.load_df(parquet_file_path, cols_names)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_cols_rowgroups(self):
        pq_obj = ParquetHandler()
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        cols_names = ['registration_dttm', 'id',
                      'first_name', 'last_name', 'gender']
        df = pq_obj.load_df(parquet_file_path, cols_names, 0)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_save_df(self):
        pq_obj = ParquetHandler()
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        df = pq_obj.load_df(parquet_file_path)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_save_df_row_group(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_save_df_compression(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_gzip.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_new_file_write(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        self.assertIsNone(pq_obj.save_df(df, new_file_path))
        os.remove(new_file_path)

    def test_write_from_df(self):
        csv_file_path = os.path.join(self.orig_base_path, 'emails.csv')
        df = pd.read_csv(csv_file_path)
        pq_obj = ParquetHandler()
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        self.assertIsNone(pq_obj.save_df(df, new_file_path))
        assert_frame_equal(df, pq_obj.load_df(new_file_path))
        os.remove(new_file_path)

    def test_invalid_base_path(self):
        with self.assertRaises(ValueError):
            ParquetHandler(base_path="some_path_abc/")
        with self.assertRaises(ValueError):
            ParquetHandler(row_group_size=-2)
        with self.assertRaises(ValueError):
            ParquetHandler(use_dictionary='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(use_deprecated_int96_timestamps='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(coerce_timestamps='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(compression='zip')

    def test_read_from_s3(self):
        s3_path = "s3://07092018pqtest/data.parquet"
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(self.parquet_basic)
        pq_obj.save_df(df, s3_path)
        reload_df = pq_obj.load_df(s3_path)
        assert_frame_equal(df, reload_df)
