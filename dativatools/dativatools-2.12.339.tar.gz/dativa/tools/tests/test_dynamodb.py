import logging
import unittest
import os
import pandas as pd
import numpy as np
from dativa.tools.aws import DynamoDB
from botocore.exceptions import ClientError
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal
from botocore.exceptions import ClientError
logger = logging.getLogger("dativa.tools.dynamodb.tests")


class DynamoDBTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_base_path = '{0}/test_data/'.format(
            os.path.dirname(os.path.abspath(__file__)))
        cls.name = 'testing_table'
        cls.df = pd.read_csv(os.path.join(cls.orig_base_path, 'dynamodb', 'email_test.csv'))
        cls.region = 'us-west-2'
        cls.hashname = 'e-mail'

    def setUp(self) -> None:
        self.ddb = DynamoDB(table_name=self.name, region=self.region, hashname=self.hashname)

    def tearDown(self):
        self.ddb.delete_table()
        try:
            self.ddb._ddb_client.describe_table(TableName=self.name)
        except self.ddb._ddb_client.exceptions.ResourceNotFoundException:
            pass

    def test_delete(self):
        """this deletes the table, the teardown then tests that deleting an already deleted table doesn't raise"""
        self.ddb.delete_table()

    def test_fails_when_writing_nan(self):
        # pd converts the blank to nan
        df = pd.read_csv(os.path.join(
            self.orig_base_path, 'dynamodb', 'email_test_with_blank.csv'))
        with self.assertRaises(ValueError):
            self.ddb.save_df(df)

    def test_fails_when_writing_blank_string(self):
        """ DynamoDB doesn't allow writing blank entries - client should pick that up"""
        df = pd.read_csv(
            os.path.join(self.orig_base_path, 'dynamodb', 'email_test_with_blank.csv'),
            keep_default_na=False)
        with self.assertRaises(ValueError):
            self.ddb.save_df(df)

    def test_write_and_readback_df_to_ddb_hash_only(self):
        """ specify only a hash  and specify a max number of records per scan to 1 - this forces it to paginate"""
        df = self.df.fillna("entry")
        self.ddb.save_df(df)
        ddb_df = self.ddb.load_df(1)
        ddb_sorted = ddb_df.astype(str).sort_values(['e-mail', 'number']).reset_index(drop=True)
        df_sorted = df.astype(str).sort_values(['e-mail', "number"]).reset_index(drop=True)
        self.assertCountEqual(df_sorted.columns, ddb_sorted.columns)
        for col in df_sorted:
            assert_series_equal(df_sorted[col], ddb_sorted[col])

    def test_failure_with_duplicate_entries_for_hash_col(self):
        """ with duplicates for hash the batchwriter will fail unless a unique range entry is specified"""
        df = pd.read_csv(os.path.join(self.orig_base_path, 'dynamodb', 'email_test_with_duplicate.csv'))
        df['e-mail'].fillna("val", inplace=True)
        with self.assertRaises(ValueError):
            self.ddb.save_df(df)

    def test_write_and_readback_df_to_ddb_hash_and_range(self):
        """ duplicates for hash column can be handled if a unique range entry is provided"""
        config = dict(table_name="temporary", region='us-west-1', hashname=self.hashname, rangename='number')
        # delete table incase it was there from previous run
        ddb_with_range = DynamoDB(**config)
        ddb_with_range.delete_table()
        # remake table and save data
        ddb_with_range = DynamoDB(**config)
        df = pd.read_csv(os.path.join(self.orig_base_path, 'dynamodb', 'email_test_with_duplicate.csv'))
        df['e-mail'].fillna("val", inplace=True)
        ddb_with_range.save_df(df)
        df_ddb = ddb_with_range.load_df()
        ddb_sorted = df_ddb.astype(str).sort_values(['e-mail', 'number']).reset_index(drop=True)
        df_sorted = df.astype(str).sort_values(['e-mail', "number"]).reset_index(drop=True)
        self.assertCountEqual(df_sorted.columns, ddb_sorted.columns)
        for col in df_sorted:
            assert_series_equal(df_sorted[col], ddb_sorted[col])

    def test_failure_with_duplicate_entries_for_range_in_each_hash(self):
        """ duplicates for hash column can be handled if a unique range entry is provided"""
        config = dict(table_name="temporary", region='us-west-1', hashname=self.hashname, rangename='number')
        ddb_with_range = DynamoDB(**config)
        df = pd.read_csv(os.path.join(self.orig_base_path, 'dynamodb', 'email_test_with_duplicate.csv'))
        df['e-mail'].fillna("val", inplace=True)
        df.loc[1, 'number'] = 0
        with self.assertRaises(ValueError):
            ddb_with_range.save_df(df)

    def test_passthrough_table(self):
        df = self.df
        ddb_passthrough = DynamoDB(
            table_name=self.name, region=self.region, hashname=self.hashname,
            table=self.ddb._table_obj)
        ddb_passthrough.save_df(df)
        ddb_df = ddb_passthrough.load_df()
        ddb_sorted = ddb_df.astype(str).sort_values(['e-mail', 'number']).reset_index(drop=True)
        df_sorted = df.astype(str).sort_values(['e-mail', "number"]).reset_index(drop=True)
        self.assertCountEqual(df_sorted.columns, ddb_sorted.columns)
        for col in df_sorted:
            assert_series_equal(df_sorted[col], ddb_sorted[col])
