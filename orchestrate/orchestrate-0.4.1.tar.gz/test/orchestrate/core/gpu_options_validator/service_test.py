import pytest
from mock import Mock, patch

from orchestrate.core.exceptions import PromptFailedException, UnsupportedOptionException
from orchestrate.core.gpu_options_validator.service import (
  FRAMEWORK_OPTION,
  RESOURCES_OPTION,
  GpuOptionsValidatorService,
)


class TestOptionsValidatorService(object):
  @pytest.fixture()
  def gpu_options_validator_service(self):
    services = Mock()
    return GpuOptionsValidatorService(services)

  def get_options_with_prompt(self, gpu_options_validator_service, options, local_run):
    with patch('orchestrate.core.gpu_options_validator.service.six.moves.input') as mock_input:
      mock_input.side_effect = EOFError("Test EOF")
      with pytest.raises(PromptFailedException):
        gpu_options_validator_service.get_framework_and_resource_options(
          options,
          local_run=local_run,
        )
      mock_input.side_effect = ['n', 'y']
      with pytest.raises(PromptFailedException):
        gpu_options_validator_service.get_framework_and_resource_options(
          options,
          local_run=local_run,
        )
      return gpu_options_validator_service.get_framework_and_resource_options(
        options,
        local_run=local_run,
      )

  @pytest.mark.parametrize(
    'input_framework,input_gpus,expected_framework,expected_resources',
    [
      (None,        None,   'python',   {}),
      (None,        0,      'python',   {'gpus': 0}),
      (None,        2,      'cuda',     {'gpus': 2}),
      ('python',    None,   'python',   {}),
      ('python',    0,      'python',   {'gpus': 0}),
      ('pytorch',   None,   'pytorch',  {'gpus': 1}),
      ('pytorch',   2,      'pytorch',  {'gpus': 2}),
    ],
  )
  def test_get_framework_and_resources_without_confirmation(
    self,
    gpu_options_validator_service,
    input_framework,
    input_gpus,
    expected_framework,
    expected_resources,
  ):
    options = {FRAMEWORK_OPTION: input_framework}
    if input_gpus is not None:
      options[RESOURCES_OPTION] = {'gpus': input_gpus}
    framework, resource_options = gpu_options_validator_service.get_framework_and_resource_options(
      options,
      local_run=False,
    )
    assert gpu_options_validator_service.services.kubernetes_service.check_gpu_nodes.call_count == int(bool(
      resource_options.get('gpus')
    ))
    assert framework == expected_framework
    assert resource_options == expected_resources

  def test_get_gpu_framework_without_gpus(self, gpu_options_validator_service):
    options = {
      FRAMEWORK_OPTION: 'pytorch',
      RESOURCES_OPTION: {'gpus': 0},
    }
    framework, resource_options = self.get_options_with_prompt(
      gpu_options_validator_service,
      options,
      local_run=False,
    )
    assert gpu_options_validator_service.services.kubernetes_service.check_gpu_nodes.call_count == 0
    assert framework == 'pytorch'
    assert resource_options == {'gpus': 0}

  def test_get_cpu_framework_with_gpus(self, gpu_options_validator_service):
    options = {
      FRAMEWORK_OPTION: 'python',
      RESOURCES_OPTION: {'gpus': 2},
    }
    framework, resource_options = self.get_options_with_prompt(
      gpu_options_validator_service,
      options,
      local_run=False,
    )
    gpu_options_validator_service.services.kubernetes_service.check_gpu_nodes.assert_called_with(2)
    assert framework == 'python'
    assert resource_options == {'gpus': 2}

  def test_get_framework_local_without_gpus(self, gpu_options_validator_service):
    options = {FRAMEWORK_OPTION: 'python'}
    framework, resource_options = gpu_options_validator_service.get_framework_and_resource_options(
      options,
      local_run=True,
    )
    assert gpu_options_validator_service.services.kubernetes_service.check_gpu_nodes.call_count == 0
    assert framework == 'python'
    assert RESOURCES_OPTION not in resource_options

  def test_get_framework_with_gpus(self, gpu_options_validator_service):
    options = {
      FRAMEWORK_OPTION: 'pytorch',
      RESOURCES_OPTION: {'gpus': 2},
    }
    with pytest.raises(UnsupportedOptionException):
      gpu_options_validator_service.get_framework_and_resource_options(
        options,
        local_run=True,
      )
