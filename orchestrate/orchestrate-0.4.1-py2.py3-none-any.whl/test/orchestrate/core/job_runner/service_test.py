import pytest
from mock import Mock

from orchestrate.core.job_runner.service import JobRunnerService
from orchestrate.core.resource.service import ResourceService


class TestJobRunnerService(object):
  @pytest.fixture
  def services(self):
    services = Mock(
      sigopt_service=Mock(api_token="sigopt_api_token")
    )
    services.resource_service = ResourceService(services)
    return services

  @pytest.fixture
  def job_runner_service(self, services):
    return JobRunnerService(services)

  def test_job_name(self, job_runner_service):
    experiment_id = '234234'
    assert job_runner_service.experiment_id(job_runner_service.job_name(experiment_id)) == experiment_id

  def test_experiment_id(self, job_runner_service):
    job_name = 'orchestrate-o3u42-owskj'
    assert job_runner_service.job_name(job_runner_service.experiment_id(job_name)) == job_name

  def test_old_job_name(self, job_runner_service):
    job_name = 'galileo-o3u42-owskj'
    assert job_runner_service.experiment_id(job_name) is None

  @pytest.mark.parametrize('resources,expected_output', [
      (
        dict(requests={'cpu': 5}),
        dict(requests={'cpu': 5}, limits=dict())
      ),
      (
        dict(requests={'cpu': '300m'}, gpus=1),
        dict(requests={'cpu': '300m'}, limits={'nvidia.com/gpu': 1})
      ),
      (
        dict(requests={'cpu': '1'}, limits={'memory': '2Gi', 'cpu': 2}, gpus=1),
        dict(requests={'cpu': '1'}, limits={'memory': '2Gi', 'cpu': 2, 'nvidia.com/gpu': 1})
      ),
  ])
  def test_format_resources(self, job_runner_service, resources, expected_output):
    actual_output = job_runner_service.format_resources(resources)
    assert actual_output == expected_output
