import json
import tempfile

import pytest
from mock import ANY, Mock, call
from sigopt.exception import ApiException
from sigopt.objects import Observation

from orchestrate.common import TemporaryDirectory
from orchestrate.runner.optimizer import MAX_METADATA_LENGTH, safe_command_string_metadata, SigOptOptimizer


class BaseOptimizerTestObject(SigOptOptimizer):
  def __init__(self, config, suggestion_path, log_path, pod_name, experiment_id, metrics=None):
    self._set_metrics = Mock()
    self.metrics = metrics or []
    super(BaseOptimizerTestObject, self).__init__(
      suggestion_path=suggestion_path,
      log_path=log_path,
      pod_name=pod_name,
      experiment_id=experiment_id,
      run_command=config['run_command'],
    )

class TestOptimizer(object):
  @pytest.mark.parametrize('cmd,expected', [
    ('', ''),
    (u'hello', u'hello'),
    ([u'true', 'false'], u'true false'),
    ('h' * MAX_METADATA_LENGTH * 2, 'h' * MAX_METADATA_LENGTH),
    (['h' * MAX_METADATA_LENGTH, 'h' * MAX_METADATA_LENGTH], 'h' * MAX_METADATA_LENGTH),
  ])
  def test_safe_command_string(self, cmd, expected):
    assert safe_command_string_metadata(cmd) == expected

  def generate_config(self, run_command=None):
    return {
      'run_command': run_command or '',
    }

  def create_optimizer(self, suggestion_path, log_path, **kwargs):
    return BaseOptimizerTestObject(
      config=self.generate_config(**kwargs),
      suggestion_path=suggestion_path,
      log_path=log_path,
      pod_name='fake_test_pod',
      experiment_id=1,
    )

  def check_observation_log(self, lines, obs_map):
    assert len(lines) == 1
    line = lines[0]
    assert line.startswith("Observation data: ")
    captured = json.loads(line[len("Observation data: "):])
    assert captured == obs_map

  @pytest.fixture
  def test_dir(self):
    with TemporaryDirectory() as tmpdir:
      yield tmpdir

  @pytest.fixture
  def suggestion_path(self, test_dir):
    return tempfile.NamedTemporaryFile('w', delete=False, dir=test_dir).name

  @pytest.fixture
  def log_path(self, test_dir):
    return tempfile.NamedTemporaryFile('w', delete=False, dir=test_dir).name

  def test_optimization_loop(self, suggestion_path, log_path):
    optimizer = self.create_optimizer(suggestion_path, log_path)
    optimizer.run_observation = Mock()
    optimizer.is_experiment_running = Mock()
    optimizer.is_experiment_running.side_effect = [True, False]
    optimizer.optimization_loop()
    optimizer.run_observation.assert_called_once_with()

  def test_run_observation(self, suggestion_path, log_path):
    optimizer = self.create_optimizer(suggestion_path, log_path)
    suggestion_json = {'id': 'test_suggestion_id'}
    optimizer.get_suggestion_json = Mock(side_effect=[suggestion_json])

    def assert_suggestion_logged():
      with open(suggestion_path) as suggestion_fp:
        assert json.load(suggestion_fp) == suggestion_json

    optimizer.run_user_command = Mock(side_effect=assert_suggestion_logged)
    optimizer.create_observation = Mock()
    optimizer.run_observation()
    optimizer.get_suggestion_json.assert_called_once_with()
    optimizer.run_user_command.assert_called_once_with()
    optimizer.create_observation.assert_called_once_with(
      suggestion_json=suggestion_json,
      parsed_logs=ANY,
      called_process_error=None,
    )

  def test_create_observation(self):
    suggestion_json = {'id': 'test_suggestion_id'}
    parsed_logs = Mock(
      failed=False,
      get_observation_data=Mock(return_value=([], {}, False, [])),
    )
    optimizer = self.create_optimizer(None, None)
    optimizer.report_observation = Mock()
    optimizer.create_observation(
      suggestion_json=suggestion_json,
      parsed_logs=parsed_logs,
      called_process_error=None,
    )
    optimizer.report_observation.assert_called_once_with(
      suggestion=suggestion_json['id'],
      values=[],
      failed=False,
      metadata={'pod_name': 'fake_test_pod'},
    )

  def test_create_failed_observation(self):
    suggestion_json = {'id': 'test_suggestion_id'}
    get_observation_data = Mock()
    get_observation_data.failed = False
    get_observation_data.side_effect = Exception("set_failed was not called")

    def set_failed():
      get_observation_data.side_effect = None
      get_observation_data.failed = True
      get_observation_data.return_value = ([], {}, True, [])

    parsed_logs = Mock(
      get_observation_data=get_observation_data,
      set_failed=Mock(side_effect=set_failed),
    )
    called_process_error = Mock(
      cmd="test command",
      returncode=1,
    )
    optimizer = self.create_optimizer(None, None)
    optimizer.report_observation = Mock()
    with pytest.warns(RuntimeWarning):
      optimizer.create_observation(
        suggestion_json=suggestion_json,
        parsed_logs=parsed_logs,
        called_process_error=called_process_error,
      )
    optimizer.report_observation.assert_called_once_with(
      suggestion=suggestion_json['id'],
      values=[],
      failed=True,
      metadata={
        'pod_name': 'fake_test_pod',
        'failed_command': called_process_error.cmd,
        'failed_return_code': called_process_error.returncode,
      },
    )

  def test_create_observation_metadata_failed(self, capsys):
    suggestion_json = {'id': 'test_suggestion_id'}
    partial_observation = {'id': 'observation_id'}
    user_metadata = {'user_meta_key': 'user_meta_value'}
    parsed_logs = Mock(
      get_observation_data=Mock(return_value=([], user_metadata, False, [])),
    )
    optimizer = self.create_optimizer(None, None)
    report_observation = Mock()

    def fail_once(**kwargs):
      report_observation.side_effect = None
      observation_dict = partial_observation.copy()
      observation_dict.update(kwargs)
      report_observation.return_value = Observation(observation_dict)
      raise ApiException({}, 400)

    report_observation.side_effect = fail_once
    optimizer.report_observation = report_observation
    with pytest.warns(RuntimeWarning):
      optimizer.create_observation(
        suggestion_json=suggestion_json,
        parsed_logs=parsed_logs,
        called_process_error=None,
      )
    assert optimizer.report_observation.mock_calls == [
      call.method(
        suggestion=suggestion_json['id'],
        values=[],
        failed=False,
        metadata=dict(pod_name='fake_test_pod', **user_metadata),
      ),
      call.method(
        suggestion=suggestion_json['id'],
        values=[],
        failed=False,
        metadata={
          'pod_name': 'fake_test_pod',
          'metadata_report_failed': 'true',
        },
      ),
    ]
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    self.check_observation_log(lines, {
      'suggestion': suggestion_json['id'],
      'values': [],
      'failed': False,
      'metadata': dict(pod_name='fake_test_pod', **user_metadata),
    })

  def test_create_observation_error(self, capsys):
    suggestion_json = {'id': 'test_suggestion_id'}
    user_metadata = {'user_meta_key': 'user_meta_value'}
    parsed_logs = Mock(
      get_observation_data=Mock(return_value=([], user_metadata, False, [])),
    )
    optimizer = self.create_optimizer(None, None)
    report_observation = Mock()

    def fail_once(**kwargs):
      report_observation.side_effect = Exception(
        "report_observation was unexpectedly called a second time"
      )
      raise ApiException({}, 500)

    report_observation.side_effect = fail_once
    optimizer.report_observation = report_observation
    with pytest.warns(RuntimeWarning), pytest.raises(ApiException):
      optimizer.create_observation(
        suggestion_json=suggestion_json,
        parsed_logs=parsed_logs,
        called_process_error=None,
      )
    optimizer.report_observation.assert_called_once_with(
      suggestion=suggestion_json['id'],
      values=[],
      failed=False,
      metadata=dict(pod_name='fake_test_pod', **user_metadata),
    )
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    self.check_observation_log(lines, {
      'suggestion': suggestion_json['id'],
      'values': [],
      'failed': False,
      'metadata': dict(pod_name='fake_test_pod', **user_metadata),
    })

  def test_create_observation_bad_params(self, capsys):
    suggestion_json = {'id': 'test_suggestion_id'}
    user_metadata = {'user_meta_key': 'user_meta_value'}
    parsed_logs = Mock(
      get_observation_data=Mock(return_value=([], user_metadata, False, [])),
    )
    optimizer = self.create_optimizer(None, None)
    report_observation = Mock()

    def fail(**kwargs):
      raise ApiException({}, 400)

    report_observation.side_effect = fail
    optimizer.report_observation = report_observation
    with pytest.warns(RuntimeWarning), pytest.raises(ApiException):
      optimizer.create_observation(
        suggestion_json=suggestion_json,
        parsed_logs=parsed_logs,
        called_process_error=None,
      )
    assert optimizer.report_observation.mock_calls == [
      call.method(
        suggestion=suggestion_json['id'],
        values=[],
        failed=False,
        metadata=dict(pod_name='fake_test_pod', **user_metadata),
      ),
      call.method(
        suggestion=suggestion_json['id'],
        values=[],
        failed=False,
        metadata={
          'pod_name': 'fake_test_pod',
          'metadata_report_failed': 'true',
        },
      ),
    ]
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    self.check_observation_log(lines, {
      'suggestion': suggestion_json['id'],
      'values': [],
      'failed': False,
      'metadata': dict(pod_name='fake_test_pod', **user_metadata),
    })
