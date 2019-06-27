from orchestrate.core.aws.service import AwsService
from orchestrate.core.custom_cluster.service import CustomClusterService
from orchestrate.core.provider.constants import Provider
from orchestrate.core.services.aws_provider_bag import AwsProviderServiceBag
from orchestrate.core.services.base import Service


class ProviderBroker(Service):
  def get_provider_service(self, provider):
    if provider == Provider.AWS:
      return AwsService(self.services, AwsProviderServiceBag(
        self.services,
        aws_access_key_id=self.services.get_option('aws.aws_access_key_id'),
        aws_secret_access_key=self.services.get_option('aws.aws_secret_access_key'),
      ))
    elif provider == Provider.CUSTOM:
      return CustomClusterService(self.services)
    else:
      raise NotImplementedError()
