from orchestrate.core.services.base import Service


class ProviderInterface(Service):
  def create_kubernetes_cluster(self, cluster_name, options):
    raise NotImplementedError()

  def destroy_kubernetes_cluster(self, cluster_name):
    raise NotImplementedError()

  def create_kubeconfig(self, cluster_name):
    raise NotImplementedError()

  def test_kubernetes_cluster(self, cluster_name):
    raise NotImplementedError()

  def create_cluster_object(self, services, name, registry):
    raise NotImplementedError()
