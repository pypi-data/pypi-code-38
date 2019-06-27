import json
import tempfile

import pytest

from orchestrate.common import safe_format
from orchestrate.runner.log_parser import LogParser


METRIC_LOG = {'type': 'metric', 'data': {
  'name': 'test_metric',
  'value': 1,
}}
METRIC_STDDEV_LOG = {'type': 'metric', 'data': {
  'name': 'test_metric_stddev',
  'value': 1,
  'value_stddev': 2,
}}
METADATA_LOG = {'type': 'metadata', 'data': {
  'key': 'metadata_key',
  'value': 'metadata_value',
}}
FAILURE_LOG = {'type': 'failed', 'data': {}}

class TestLogParser(object):
  @pytest.fixture
  def log_path(self):
    with tempfile.NamedTemporaryFile('w') as temp_fp:
      yield temp_fp.name

  def write_logs(self, logs, log_path):
    with open(log_path, 'a') as log_fp:
      for log in logs:
        json.dump(log, log_fp)
        log_fp.write('\n')

  def test_metric_log(self, log_path):
    self.write_logs([METRIC_LOG], log_path)
    parsed = LogParser(log_path, metrics=[METRIC_LOG['data']])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == [{
      'name': METRIC_LOG['data']['name'],
      'value': METRIC_LOG['data']['value'],
      'value_stddev': None,
    }]
    assert metadata == {}
    assert failed is False
    assert missing_metrics == []

  def test_metric_stddev_log(self, log_path):
    self.write_logs([METRIC_STDDEV_LOG], log_path)
    parsed = LogParser(log_path, metrics=[METRIC_STDDEV_LOG['data']])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == [METRIC_STDDEV_LOG['data']]
    assert metadata == {}
    assert failed is False
    assert missing_metrics == []

  def test_missing_metric(self, log_path):
    parsed = LogParser(log_path, metrics=[METRIC_LOG['data']])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert missing_metrics == [METRIC_LOG['data']['name']]
    assert failed is True
    assert metadata == {}

  def test_extra_metric(self, log_path):
    self.write_logs([METRIC_STDDEV_LOG], log_path)
    parsed = LogParser(log_path, metrics=[])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert missing_metrics == []
    assert failed is False
    meta_metric_name = METRIC_STDDEV_LOG['data']['name']
    meta_stddev_name = safe_format('{}_stddev', meta_metric_name)
    assert metadata == {
      meta_metric_name: METRIC_STDDEV_LOG['data']['value'],
      meta_stddev_name: METRIC_STDDEV_LOG['data']['value_stddev'],
    }

  def test_overwrite_metric(self, log_path):
    self.write_logs([METRIC_LOG, METRIC_LOG], log_path)
    with pytest.warns(RuntimeWarning):
      parsed = LogParser(log_path, metrics=[METRIC_LOG['data']])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == [{
      'name': METRIC_LOG['data']['name'],
      'value': METRIC_LOG['data']['value'],
      'value_stddev': None,
    }]
    assert metadata == {}
    assert failed is False
    assert missing_metrics == []

  def test_failure(self, log_path):
    self.write_logs([FAILURE_LOG], log_path)
    parsed = LogParser(log_path, metrics=[])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert metadata == {}
    assert failed is True
    assert missing_metrics == []

  def test_failure_with_metric(self, log_path):
    self.write_logs([METRIC_LOG, FAILURE_LOG], log_path)
    parsed = LogParser(log_path, metrics=[METRIC_LOG['data']])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert metadata == {
      METRIC_LOG['data']['name']: METRIC_LOG['data']['value'],
    }
    assert failed is True
    assert missing_metrics == []

  def test_metadata_log(self, log_path):
    self.write_logs([METADATA_LOG], log_path)
    parsed = LogParser(log_path, metrics=[])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert metadata == {
      METADATA_LOG['data']['key']: METADATA_LOG['data']['value'],
    }
    assert failed is False
    assert missing_metrics == []

  def test_overwrite_metdata(self, log_path):
    self.write_logs([METADATA_LOG, METADATA_LOG], log_path)
    with pytest.warns(RuntimeWarning):
      parsed = LogParser(log_path, metrics=[])
    value_list, metadata, failed, missing_metrics = parsed.get_observation_data()
    assert value_list == []
    assert metadata == {
      METADATA_LOG['data']['key']: METADATA_LOG['data']['value'],
    }
    assert failed is False
    assert missing_metrics == []
