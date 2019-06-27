from orchestrate.core.cluster.service import ClusterService
from orchestrate.core.cluster_metadata.service import ClusterMetadataService
from orchestrate.core.docker.service import DockerService
from orchestrate.core.gpu_options_validator.service import GpuOptionsValidatorService
from orchestrate.core.job_logs.service import JobLogsService
from orchestrate.core.job_runner.service import JobRunnerService
from orchestrate.core.job_status.service import JobStatusService
from orchestrate.core.kubectl.service import KubectlService
from orchestrate.core.kubernetes.service import KubernetesService
from orchestrate.core.logging.service import LoggingService
from orchestrate.core.model_packer.service import ModelPackerService
from orchestrate.core.options_validator.service import OptionsValidatorService
from orchestrate.core.provider.broker import ProviderBroker
from orchestrate.core.resource.service import ResourceService
from orchestrate.core.services.bag import ServiceBag
from orchestrate.core.sigopt.service import SigOptService
from orchestrate.core.template.service import TemplateService


class OrchestrateServiceBag(ServiceBag):
  def __init__(self, options):
    self._options = options
    super(OrchestrateServiceBag, self).__init__()

  @property
  def options(self):
    return self._options

  def get_option(self, name):
    parts = name.split('.')
    options = self.options

    for part in parts:
      try:
        options = options[part]
      except (KeyError, TypeError):
        return None
    return options

  def _create_services(self):
    super(OrchestrateServiceBag, self)._create_services()
    self.resource_service = ResourceService(self)
    self.provider_broker = ProviderBroker(self)
    self.cluster_metadata_service = ClusterMetadataService(self)
    self.cluster_service = ClusterService(self)
    self.docker_service = DockerService(self)
    self.job_runner_service = JobRunnerService(self)
    self.job_logs_service = JobLogsService(self)
    self.job_status_service = JobStatusService(self)
    self.kubectl_service = KubectlService(self)
    self.kubernetes_service = KubernetesService(self)
    self.logging_service = LoggingService(self)
    self.model_packer_service = ModelPackerService(self)
    self.options_validator_service = OptionsValidatorService(self)
    self.gpu_options_validator_service = GpuOptionsValidatorService(self)
    self.template_service = TemplateService(self)
    self.sigopt_service = SigOptService(self, api_token=self.get_option('sigopt.api_token'))

  def _warmup_services(self):
    super(OrchestrateServiceBag, self)._warmup_services()
    self.kubernetes_service.warmup()
