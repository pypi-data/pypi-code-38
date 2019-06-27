import io
import unittest
from unittest.mock import patch, PropertyMock
import pandas as pd
import pyarrow as pa
from pandas.api.types import is_numeric_dtype
import datasetmaker as dam
from .mock_data import (
    mock_skv_schema,
    mock_skv_xml,
    mock_frame)


class TestSKVClient(unittest.TestCase):
    def setUp(self):
        """Patch all IO functions."""

        p = 'datasetmaker.sources.skolverket.SKVClient.schema'
        schema_patcher = patch(p, new_callable=PropertyMock)
        schema = schema_patcher.start()
        schema.return_value = mock_skv_schema
        self.addCleanup(schema_patcher.stop)

        p = 'datasetmaker.sources.skolverket.Table._fetch_xml'
        fetch_patcher = patch(p)
        fetch = fetch_patcher.start()
        fetch.return_value = mock_skv_xml
        self.addCleanup(fetch_patcher.stop)

        p = 'datasetmaker.sources.skolverket.Table._read_table'
        read_patcher = patch(p)
        read = read_patcher.start()
        read.return_value = pa.Table.from_pandas(
            pd.read_csv(io.StringIO(mock_frame)))
        self.addCleanup(read_patcher.stop)

        p = 'datasetmaker.sources.skolverket.Table._write_table'
        write_patcher = patch(p)
        write_patcher.start()
        self.addCleanup(write_patcher.stop)

        self.client = dam.create_client(source='skolverket')

    def test_list_indicators(self):
        indicators = self.client.indicators
        self.assertIn('and_beh_yrk_exklok__139', indicators)

    def test_get_indicators(self):
        data = self.client.get(indicators=['sva_andel_hojt__83'], years=[2017])
        self.assertIn('sva_andel_hojt__83', data)

    def test_fails_if_wrong_indicator(self):
        with self.assertRaises(ValueError):
            self.client.get(indicators=['does_not_exist'], years=[2015])

    def test_year_not_available(self):
        with self.assertRaises(ValueError):
            self.client.get(indicators=['sva_andel_hojt__83'], years=[1576])

    def test_type_conversion(self):
        data = self.client.get(indicators=['en_antal_m_betyg__83'],
                               years=[2018])
        self.assertTrue(is_numeric_dtype(data['en_antal_m_betyg__83']))

    def test_column_name_standardization(self):
        """Check that `skol_kod` was properly translated to school"""
        data = self.client.get(indicators=['en_antal_m_betyg__83'],
                               years=[2017])
        self.assertIn('school', data.reset_index().columns)
