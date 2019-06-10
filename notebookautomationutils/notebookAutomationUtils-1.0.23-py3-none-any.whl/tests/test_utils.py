import os
import utils.utils as utils
import unittest
import pandas as pd
from unittest.mock import patch, Mock
from unittest import TestCase

class TestUtils(TestCase):
    """
    Tests for utils
    """
    def test_search_for_file(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"
        expected = 'File_Data.csv'
        result = utils.search_for_file(dirpath, ".csv", "Data")
        assert result == (expected)


    def test_search_for_file_uppercase(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"
        expected = 'File_Data.csv'
        result = utils.search_for_file(dirpath, ".csv", "DATA")
        assert result == expected


    def test_search_for_file_not_found(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"
        expected = None
        result = utils.search_for_file(dirpath, ".csv", "abc")
        assert result == expected     

    
    def test_load_file(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"
        
        expected = pd.read_csv(dirpath + "/" + "File_Data.csv", parse_dates=['_time'], index_col='_time', header=0)
        data = utils.load_file(dirpath, "File_Data.csv")
        pd.testing.assert_frame_equal(data, expected)
          
    
    def test_load_file_wrong_path(self):
        dirpath = "abc/"
        
        with self.assertRaises(FileNotFoundError) as cm:
            utils.load_file(dirpath, "File_Data.csv")
        self.assertEqual(cm.exception.__class__, FileNotFoundError)


    def test_agg(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"
        
        file = utils.load_file(dirpath, "File_Data.csv")
        result = utils.my_agg(file)

        expected = pd.Series({'P50': 2300.0, 'P95': 2300.0}, name=None)
        pd.testing.assert_series_equal(result, expected)