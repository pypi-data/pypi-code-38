import json
from test.orchestrate.io.test_base import IoTestBase

import numpy as np
import pytest


class TestLogger(IoTestBase):
  def test_log_to_logfile_io_enabled(self, logger_io_enabled, log_path):
    logger_io_enabled.write_log('test', {'key': 'value'})
    with open(log_path) as log_fp:
      assert json.load(log_fp) == {'type': 'test', 'data': {'key': 'value'}}

  def test_no_print_io_enabled(self, capsys, logger_io_enabled, log_path):
    logger_io_enabled.write_log('test', {'key': 'value'})
    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err

  def test_log_to_stdout_io_disabled(self, capsys, logger_io_disabled, log_path):
    logger_io_disabled.write_log('test', {'key': 'value'})
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'type': 'test', 'data': {'key': 'value'}}
    assert not captured.err

  @pytest.mark.parametrize('metric_value', [3, '7', 7.00972, np.float32(29)])
  def test_log_metric(self, logger_io_enabled, log_path, metric_value):
    logger_io_enabled.log_metric('metric_name', metric_value)
    with open(log_path) as log_fp:
      assert json.load(log_fp) == {
        'type': 'metric',
        'data': {
          'name': 'metric_name',
          'value': float(metric_value),
        }
      }

  def test_log_bad_metric_name(self, logger_io_disabled):
    with pytest.raises(ValueError):
      logger_io_disabled.log_metric(1, 1)

  @pytest.mark.parametrize('metric_value', ['hello', [1, 2, 3], {}, np.array([29, 30])])
  def test_log_bad_metric_value(self, logger_io_disabled, log_path, metric_value):
    with pytest.raises(ValueError):
      logger_io_disabled.log_metric('metric_name', metric_value)

  @pytest.mark.parametrize('metric_stddev', [3, '7', 7.00972, np.float32(29)])
  def test_log_metric_stddev(self, logger_io_enabled, log_path, metric_stddev):
    logger_io_enabled.log_metric('metric_name', 1, stddev=metric_stddev)
    with open(log_path) as log_fp:
      assert json.load(log_fp) == {
        'type': 'metric',
        'data': {
          'name': 'metric_name',
          'value': 1,
          'value_stddev': float(metric_stddev),
        }
      }

  @pytest.mark.parametrize('metric_stddev', [
    'hello',
    [1, 2, 3],
    {},
    np.array([29, 30]),
    float('nan'),
    float('-inf'),
  ])
  def test_log_bad_stddev(self, logger_io_enabled, log_path, metric_stddev):
    with pytest.raises(ValueError):
      logger_io_enabled.log_metric('metric_name', 1, stddev=metric_stddev)

  @pytest.mark.parametrize('metadata_value,metadata_log', [
    (5, 5),
    (np.float32(20), 20),
    ('hello', 'hello'),
    ({}, '{}'),
    (float('nan'), 'nan'),
    (float('-inf'), '-inf'),
  ])
  def test_log_metadata(self, logger_io_enabled, log_path, metadata_value, metadata_log):
    logger_io_enabled.log_metadata('metadata_key', metadata_value)
    with open(log_path) as log_fp:
      assert json.load(log_fp) == {
        'type': 'metadata',
        'data': {
          'key': 'metadata_key',
          'value': metadata_log,
        }
      }

  def test_log_bad_metadata_key(self, logger_io_disabled, log_path):
    with pytest.raises(ValueError):
      logger_io_disabled.log_metadata(1, 1)

  def test_log_failure(self, logger_io_enabled, log_path):
    logger_io_enabled.log_failure()
    with open(log_path) as log_fp:
      assert json.load(log_fp) == {
        'type': 'failed',
        'data': {}
      }
