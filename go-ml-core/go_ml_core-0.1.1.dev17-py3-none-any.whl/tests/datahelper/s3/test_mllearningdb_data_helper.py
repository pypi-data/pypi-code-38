import pytest
from mlcore.datahelper.s3.mllearningdb_data_helper import DataHelper
from config.get_config import get_config

class TestDataHelper:

    def test_get_latest_s3key(self):
        config = get_config('./config/config_dev.yml')
        data_helper = DataHelper(config)

        keys = [
            'test-workspace/2019-01-14T07:42:47/data.json',
            'test-workspace/2019-01-14T07:42:47/_SUCCESS',
            'test-workspace/2019-01-14T08:42:47/data.json',
            'test-workspace/2019-01-14T08:42:47/_SUCCESS',
            'test-workspace/2019-01-13T09:42:47/data.json',
            'test-workspace/2019-01-13T09:42:47/_SUCCESS',
            'test-workspace/2019-01-15T13:42:47/data.json'
        ]
        assert DataHelper(config).get_latest_s3key(keys) == 'test-workspace/2019-01-14T08:42:47/data.json'

    def test_get_latest_job_s3key(self):
        config = get_config('./config/config_dev.yml')
        data_helper = DataHelper(config)

        keys = [
            'test-workspace/2019-01-14T07:42:47/data.json',
            'test-workspace/2019-01-14T07:42:47/_SUCCESS',
            'test-workspace/2019-01-14T08:42:47/data.json',
            'test-workspace/2019-01-14T08:42:47/_SUCCESS',
            'test-workspace/2019-01-13T09:42:47/data.json',
            'test-workspace/2019-01-13T09:42:47/_SUCCESS',
            'test-workspace/2019-01-15T13:42:47/data.json'
        ]
        assert DataHelper(config).get_latest_job_s3key(keys) == 'test-workspace/2019-01-14T08:42:47/data.json'
    
    def test_get_latest_etl_s3key(self):
        config = get_config('./config/config_dev.yml')
        data_helper = DataHelper(config)

        keys = [
            'test-workspace/2019-01-14T07:42:47/data.json',
            'test-workspace/2019-01-14T07:42:47/_SUCCESS',
            'test-workspace/2019-01-14T08:42:47/data.json',
            'test-workspace/2019-01-14T08:42:47/_SUCCESS',
            'test-workspace/2019-01-13T09:42:47/data.json',
            'test-workspace/2019-01-13T09:42:47/_SUCCESS',
            'test-workspace/2019-01-15T13:42:47/data.json'
        ]
        assert DataHelper(config).get_latest_etl_s3key(keys) == 'test-workspace/2019-01-14T08:42:47/data.json'


    def test_get_dt_str_by_timestamp(self):
        config = get_config('./config/config_dev.yml')
        data_helper = DataHelper(config)


        dt_str = data_helper.get_dt_str_by_timestamp(1547451767)
        assert dt_str['dt'] == '2019-01-14T07:42:47'
        assert dt_str['dt_hour_str'] == '2019-01-14T07'
        assert dt_str['dt_minute_str'] == '2019-01-14T07:42'
        assert dt_str['time_str'] == '07:42:47'

