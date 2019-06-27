import six

from orchestrate.common import safe_format
from orchestrate.core.cluster.context import DisconnectOnException
from orchestrate.core.cluster.errors import *
from orchestrate.core.provider.constants import Provider, string_to_provider
from orchestrate.core.services.base import Service


class ClusterService(Service):
  def connected_clusters(self):
    return self.services.kubernetes_service.get_cluster_names()

  def assert_is_connected(self):
    connected_clusters = self.connected_clusters()
    if not connected_clusters:
      raise NotConnectedError()
    elif len(connected_clusters) > 1:
      raise MultipleClustersConnectionError(connected_clusters)
    return connected_clusters[0]

  def assert_is_disconnected(self):
    connected_clusters = self.connected_clusters()
    if connected_clusters:
      if len(connected_clusters) == 1:
        raise PleaseDisconnectError(connected_clusters[0])
      else:
        raise MultipleClustersConnectionError(connected_clusters)

  def connect(self, cluster_name, provider_string, kubeconfig, registry):
    try:
      self.assert_is_disconnected()
    except PleaseDisconnectError as e:
      if e.current_cluster_name == cluster_name:
        raise AlreadyConnectedException(e.current_cluster_name)
      else:
        raise

    provider = string_to_provider(provider_string)
    provider_service = self.services.provider_broker.get_provider_service(provider)

    if kubeconfig is None:
      kubeconfig = provider_service.create_kubeconfig(cluster_name)
    else:
      assert provider == Provider.CUSTOM, "Must use --provider custom to connect with a kubeconfig"

    with DisconnectOnException(cluster_name, self.services):
      self.services.kubernetes_service.write_config(cluster_name, kubeconfig)
      self.services.kubernetes_service.ensure_orchestrate_namespace()
      cluster = provider_service.create_cluster_object(
        services=self.services,
        name=cluster_name,
        registry=registry,
      )
      self.services.cluster_metadata_service.write_metadata(cluster)
      return self.test()

  def create(self, options):
    try:
      self.assert_is_disconnected()
    except PleaseDisconnectError as e:
      if e.current_cluster_name == options.get('cluster_name', ''):
        raise AlreadyConnectedException(e.current_cluster_name)
      else:
        raise

    self.services.options_validator_service.validate_cluster_options(**options)
    cluster_name = options.get('cluster_name', '')

    provider_string = options.get('provider', '')
    provider = string_to_provider(provider_string)
    provider_service = self.services.provider_broker.get_provider_service(provider)

    with DisconnectOnException(cluster_name, self.services):
      cluster = provider_service.create_kubernetes_cluster(options)
      self.services.kubernetes_service.ensure_orchestrate_namespace()
      self.services.cluster_metadata_service.write_metadata(cluster)
      self.services.kubernetes_service.wait_until_nodes_are_ready()
      return cluster.name

  def destroy(self, cluster_name, provider_string):
    # TODO(alexandra): if we require that you are connected to a cluster to delete it, then we could read provider
    # from the metadata
    provider = string_to_provider(provider_string)
    provider_service = self.services.provider_broker.get_provider_service(provider)
    self.services.cluster_metadata_service.ensure_metadata_deleted(cluster_name=cluster_name)
    provider_service.destroy_kubernetes_cluster(cluster_name=cluster_name)

  def disconnect(self, cluster_name, disconnect_all):
    if (cluster_name and disconnect_all) or (not cluster_name and not disconnect_all):
      raise ClusterError('Must provide exactly one of --cluster-name <cluster_name> and --all')

    try:
      current_cluster_name = self.assert_is_connected()
      if cluster_name is not None and current_cluster_name != cluster_name:
        raise PleaseDisconnectError(current_cluster_name)
    except MultipleClustersConnectionError:
      if not disconnect_all:
        raise

    for cname in self.connected_clusters():
      try:
        self.services.cluster_metadata_service.ensure_metadata_deleted(cluster_name=cname)
        self.services.kubernetes_service.ensure_config_deleted(cluster_name=cname)
      except Exception as e:
        six.raise_from(ClusterError(safe_format(
          'Looks like an error occured while attempting to disconnect from cluster "{}".',
          cname,
        )), e)

  def test(self):
    cluster_name = self.assert_is_connected()
    cluster = self.services.cluster_metadata_service.read_metadata(cluster_name)
    provider_service = self.services.provider_broker.get_provider_service(cluster.provider)

    try:
      provider_service.test_kubernetes_cluster(cluster_name=cluster.name)
    except Exception as e:
      six.raise_from(ClusterError(safe_format(
        'Looks like an error occured while testing cluster "{}".',
        cluster.name,
      )), e)

    return cluster
