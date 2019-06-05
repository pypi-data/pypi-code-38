import os
import unittest
import utils.utils as utils
import main.generate_metrics as gm
from unittest.mock import patch, Mock
from unittest import TestCase

class TestGenerateMetrics(TestCase):
    """
    Tests for MetricGenerator class
    """
    def test_generate_bootstrap_metric_null_data(self):
        # MetricGenerator should be passed any version number (can be dummy) for testing
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_bootstrap_metric(None, 10000, 10, 3500)
        assert result == None

    def test_generate_object_home_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_object_home_metric(None, 10000, 10, 3500)
        assert result == None

    def test_generate_rh_cold_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_rh_cold_metric(None, 10000, 10)
        assert result == None

    def test_generate_rh_warm_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_rh_warm_metric(None, 10000, 10)
        assert result == None

    def test_generate_mainfeed_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_mainfeed_metric(None, 10000, 10, 3500)
        assert result == None

    def test_generate_cold_start_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_cold_start_metric(None, 10000, 10, 3000)
        assert result == None

    def test_generate_app_start_metric_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_app_start_metric(None, 10000, 10, 3000)
        assert result == None    

    def test_aggregate_by_network_appver_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.aggregate_by_network_appver(None, 10000, 10)
        assert result == None    

    def test_aggregate_by_fields_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.aggregate_by_fields(None, 10000, 10, [])
        assert result == None   
    
    def test_verify_sla_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.verify_sla(None, 2000)
        assert result == None

    def test_verify_sla_for_entitytype_null_data(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.verify_sla_for_entitytype(None, 2000)
        assert result == None

    def test_load_data_from_folder_incorrect(self):
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        data = m.load_data_from_folder("/")
        expected = {'AppStart': None,
            'Bootstrap': None,          
            'ColdStart': None,
            'MainFeed': None,
            'OH': None}
        assert data == expected

    def test_generate_bootstrap_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_bootstrap_metric(data, 10000, 10, 3500)
        assert result == None
    
    def test_generate_object_home_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_object_home_metric(data, 10000, 10, 3500)
        assert result == None

    def test_generate_rh_cold_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_rh_cold_metric(data, 10000, 10)
        assert result == None
    
    def test_generate_rh_warm_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_rh_warm_metric(data, 10000, 10)
        assert result == None
    
    def test_generate_mainfeed_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_mainfeed_metric(data, 10000, 10, 3500)
        assert result == None

    def test_generate_cold_start_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_cold_start_metric(data, 10000, 10, 3000)
        assert result == None
    
    def test_generate_app_start_metric_incorrect_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        m = gm.MetricGenerator("iOS", '17.0(6136089)', '16.3(6135950)')
        result = m.generate_app_start_metric(data, 10000, 10, 3000)
        assert result == None