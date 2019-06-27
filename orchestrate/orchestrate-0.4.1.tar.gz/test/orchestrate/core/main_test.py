import os
import uuid
from tempfile import NamedTemporaryFile

import pytest
from mock import Mock, patch

from orchestrate.common import safe_format
from orchestrate.core.cluster.object import CustomCluster
from orchestrate.core.main import OrchestrateApp
from orchestrate.core.paths import get_executable_path


# From cement docs: http://builtoncement.com/2.10/dev/testing.html
class OrchestrateTestApp(OrchestrateApp):
  class Meta(object):
    argv = []
    config_files = []


class TestOrchestrateCommands(object):
  app_class = OrchestrateTestApp

  @pytest.mark.skip(reason="Need to mock")
  def test_orchestrate_run(self, tmpdir):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['init', '--directory', tmpdir]) as app:
        app.run()
    assert e.value.code == 0

    with \
      patch('orchestrate.core.run.sigopt.Connection') as mock_conn, \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['run', '--filename', safe_format('{}/orchestrate.yml', tmpdir)]) as app:
        mock_conn.return_value = Mock(
          experiments=Mock(
            return_value=Mock(
              create=Mock(
                return_value=Mock(id=uuid.uuid4())
              )
            )
          )
        )
        app.run()
      assert mock_conn.called
    assert e.value.code == 0

    os.remove(safe_format('{}/orchestrate.yml', tmpdir))

  def test_orchestrate_version(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['version']) as app:
        app.run()
    assert e.value.code == 0

  def test_orchestrate_init(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['init']) as app:
        app.run()
    assert e.value.code == 0

  def test_orchestrate_status(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['status']) as app:
        app.run()
    assert e.value.code == 2

  @pytest.mark.skip(reason='job for 123 does not exist')
  def test_orchestrate_status_with_args(self):
    with OrchestrateTestApp(argv=['status', '123']) as app:
      with pytest.raises(NotImplementedError) as e:
        app.run()
      assert e.value.args[0] == "Status: 123"

  def test_orchestrate_logs(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['logs']) as app:
        app.run()
    assert e.value.code == 2

  @pytest.mark.skip(reason='job for 123 does not exist')
  def test_orchestrate_logs_with_args(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['logs', '123']) as app:
        app.run()
    assert e.value.code == 0

  def test_orchestrate_test(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['test']) as app:
        app.run()
    assert e.value.code == 0

  def test_orchestrate_kubectl(self):
    kubectl_env_dict = {
      'KUBECONFIG': 'dummy_kubeconfig',
      'PATH': '/dummy/bin',
    }
    with \
      patch('os.execvpe') as mock_execvpe, \
      patch('orchestrate.core.kubectl.service.KubectlService.kubectl_env', side_effect=kubectl_env_dict), \
      patch('orchestrate.core.cluster.service.ClusterService.assert_is_connected', return_value='foobar'), \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['kubectl', 'get', '-h']) as app:
        app.run()
      exec_path = get_executable_path('kubectl')
      assert mock_execvpe.called_once_with(
        exec_path,
        [exec_path, 'get', '-h'],
        env=kubectl_env_dict,
      )
    assert e.value.code == 0

  def test_fake_clean(self):
    with \
      patch('orchestrate.core.docker.service.DockerService.clean') as mock_clean, \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['clean']) as app:
        app.run()
      mock_clean.assert_called_once_with(remove_current_frameworks=False)
    assert e.value.code == 0
    with \
      patch('orchestrate.core.docker.service.DockerService.clean') as mock_clean, \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['clean', '--all']) as app:
        app.run()
      mock_clean.assert_called_once_with(remove_current_frameworks=True)
    assert e.value.code == 0

  def test_unknown_arg(self):
    with pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['status-all', 'bogus', '--option']) as app:
        app.run()
    assert e.value.code == 2

class TestOrchestrateClusterCommands(object):
  app_class = OrchestrateTestApp

  def test_cluster_connect(self):
    with \
      patch('orchestrate.core.main.OrchestrateServiceBag', return_value=Mock()), \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['cluster', 'connect', '-n', 'foobar', '--provider', 'custom']) as app:
        app.run()
    assert e.value.code == 0

  def test_cluster_create(self):
    with NamedTemporaryFile('r') as f:
      with \
        patch('orchestrate.core.main.OrchestrateServiceBag', return_value=Mock()), \
        pytest.raises(SystemExit) as e:
        with OrchestrateTestApp(argv=['cluster', 'create', '-f', f.name]) as app:
          app.run()
    assert e.value.code == 0

  def test_cluster_destroy(self):
    with \
      patch('orchestrate.core.main.OrchestrateServiceBag', return_value=Mock()), \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['cluster', 'destroy', '-n', 'foobar', '--provider', 'aws']) as app:
        app.run()
    assert e.value.code == 0

  def test_cluster_disconnect(self):
    with \
      patch('orchestrate.core.main.OrchestrateServiceBag', return_value=Mock()), \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['cluster', 'disconnect', '-n', 'foobar']) as app:
        app.run()
    assert e.value.code == 0

  def test_cluster_test(self):
    mock_services = Mock()
    mock_services.cluster_service.test.return_value = CustomCluster(
      services=mock_services,
      name='foobar',
      registry=None,
    )
    with \
      patch('orchestrate.core.main.OrchestrateServiceBag', return_value=mock_services), \
      pytest.raises(SystemExit) as e:
      with OrchestrateTestApp(argv=['cluster', 'test']) as app:
        app.run()
    assert e.value.code == 0
