from orchestrate.common import safe_format
from orchestrate.core.cluster.object import CustomCluster
from orchestrate.core.exceptions import OrchestrateException
from orchestrate.core.provider.constants import Provider, provider_to_string
from orchestrate.core.provider.interface import ProviderInterface


class CustomClusterService(ProviderInterface):
  def create_kubernetes_cluster(self, cluster_name, options):
    raise OrchestrateException(safe_format(
      'When you use provider = "{}", we assume that you have created your own kubernetes cluster.'
      ' If you are attempting to connect to a custom cluster that you have already created, please use:'
      '\nsigopt cluster connect --provider custom --kubeconfig <kubeconfig> --cluster-name {}',
      provider_to_string(Provider.CUSTOM),
      cluster_name,
    ))

  def destroy_kubernetes_cluster(self, cluster_name):
    raise OrchestrateException(safe_format(
      'When you use provider = "{}", we assume that you have created your own kubernetes cluster.'
      ' If you are attempting to disconnect from a custom cluster that you have already created, please use:'
      '\nsigopt cluster disconnect --cluster-name {}',
      provider_to_string(Provider.CUSTOM),
      cluster_name,
    ))

  def create_kubeconfig(self, cluster_name):
    raise OrchestrateException(safe_format(
      'When you use provider = "{}", we assume that you have created your own kubernetes cluster.'
      ' Additionally we assume that you have a copy of the kubeconfig file that is used to access the cluster.'
      ' Please provider the path to the kubeconfig as an arguement, as you see below:'
      '\nsigopt cluster connect --provider custom --kubeconfig <kubeconfig> --cluster-name {}',
      provider_to_string(Provider.CUSTOM),
      cluster_name,
    ))

  def test_kubernetes_cluster(self, cluster_name):
    self.services.kubernetes_service.test_config()

  def create_cluster_object(self, services, name, registry):
    return CustomCluster(
      services=services,
      name=name,
      registry=registry,
    )
