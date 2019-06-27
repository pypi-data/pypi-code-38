import pytest
from mock import Mock, patch

from orchestrate.core.kubectl.service import KubectlError, KubectlService


DUMMY_RETURN_VALUE = object()


class TestKubectlService(object):
  @pytest.fixture()
  def kubectl_service(self):
    services = Mock()
    services.kubernetes_service.kube_config = 'test_config'
    return KubectlService(services)

  def mock_popen(self, return_code, out_msg, err_msg=None):

    def popen(*args, **kwargs):
      stdout = kwargs.pop('stdout')
      stdout.write(out_msg)
      if err_msg:
        stderr = kwargs.pop('stderr')
        stderr.write(err_msg)
      return Mock(wait=Mock(return_value=return_code))

    return Mock(side_effect=popen)

  def test_kubectl(self, kubectl_service):
    with patch('orchestrate.core.kubectl.service.subprocess') as mock_subprocess:
      mock_subprocess.Popen = self.mock_popen(0, 'DUMMY_RETURN_VALUE')
      assert kubectl_service.kubectl(['foo'], decode_json=False) == 'DUMMY_RETURN_VALUE'
      assert mock_subprocess.Popen.call_args[0][0] == ['kubectl', 'foo']

  def test_kubectl_json(self, kubectl_service):
    with patch('orchestrate.core.kubectl.service.subprocess') as mock_subprocess:
      mock_subprocess.Popen = self.mock_popen(0, '{"foo": "bar"}')
      assert kubectl_service.kubectl(['foo'], decode_json=True) == dict(foo='bar')
      assert mock_subprocess.Popen.call_args[0][0] == ['kubectl', 'foo', '-o', 'json']

  def test_kubectl_error(self, kubectl_service):
    with patch('orchestrate.core.kubectl.service.subprocess') as mock_subprocess:
      return_code = 1
      out_msg = "Test kubectl output"
      err_msg = "Test kubectl error"
      mock_subprocess.Popen = self.mock_popen(return_code, out_msg, err_msg)
      with pytest.raises(KubectlError) as excinfo:
        kubectl_service.kubectl(['foo'], decode_json=False)
      assert excinfo.value.return_code == return_code
      assert excinfo.value.stdout == out_msg
      assert excinfo.value.stderr == err_msg
