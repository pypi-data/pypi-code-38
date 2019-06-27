import pytest

from orchestrate.core.services.orchestrate_bag import OrchestrateServiceBag


class TestOrchestrateServiceBag(object):
  # Requires that we set the correct environment variables in travis
  def test_orchestrate_service_bag(self):
    services = OrchestrateServiceBag(options=None)
    assert services.cluster_metadata_service is not None
    assert services.cluster_service is not None
    assert services.docker_service is not None
    assert services.job_logs_service is not None
    assert services.job_runner_service is not None
    assert services.job_status_service is not None
    assert services.kubectl_service is not None
    assert services.kubernetes_service is not None
    assert services.logging_service is not None
    assert services.model_packer_service is not None
    assert services.options_validator_service is not None
    assert services.provider_broker is not None
    assert services.resource_service is not None
    assert services.sigopt_service is not None
    assert services.sigopt_service.conn is not None
    assert services.template_service is not None

  @pytest.mark.parametrize('options', [
    None,
    dict(),
    dict(sigopt=None),
    dict(sigopt=dict(api_token=None)),
  ])
  def test_get_option_does_not_exist(self, options):
    services = OrchestrateServiceBag(options)
    assert services.get_option('sigopt.api_token') is None

  @pytest.mark.parametrize('options', [
    dict(sigopt=dict(api_token='foobar', dev_token='barfoo')),
    dict(sigopt=dict(api_token='foobar')),
  ])
  def test_get_option_does_exist(self, options):
    services = OrchestrateServiceBag(options)
    assert services.get_option('sigopt.api_token') == 'foobar'
