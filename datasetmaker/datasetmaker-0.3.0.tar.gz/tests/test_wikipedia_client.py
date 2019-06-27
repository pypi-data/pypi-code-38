import io
import unittest
from unittest.mock import patch, PropertyMock
import pandas as pd
import datasetmaker as dam
from .mock_wikipedia_data import mock_election_tables, mock_elections_html


class TestWikipediaClient(unittest.TestCase):
    def setUp(self):
        self.client = dam.create_client(source='wikipedia')

    def test_test(self):
        dam.sources.wikipedia.url = io.StringIO(mock_elections_html)
        df = self.client.get(indicators=['wp_parl_prev'], years=[2016])
        self.assertTrue(type(df) is pd.DataFrame)
