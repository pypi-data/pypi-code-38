from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException


class ClusterError(OrchestrateException):
  pass


class MultipleClustersConnectionError(ClusterError):
  def __init__(self, connected_clusters):
    super(MultipleClustersConnectionError, self).__init__(
      safe_format(
        "You are currently connected to more than one cluster, all of which are listed below."
        "\nPlease disconnect from some of these clusters before re-running your command."
        "\nConnected clusters:"
        ":\n\t{}",
        "\n\t".join(connected_clusters),
      )
    )


class PleaseDisconnectError(ClusterError):
  def __init__(self, current_cluster_name):
    super(PleaseDisconnectError, self).__init__(
      safe_format("Please disconnect from this cluster before re-running your command: {}", current_cluster_name)
    )
    self.current_cluster_name = current_cluster_name


class NotConnectedError(ClusterError):
  def __init__(self):
    super(NotConnectedError, self).__init__("You are not currently connected to any cluster")


class AlreadyConnectedException(ClusterError):
  def __init__(self, current_cluster_name):
    super(AlreadyConnectedException, self).__init__(
      safe_format(
        "You are already connected this cluster: {}."
        " Please `sigopt cluster test` to verify the details of your connection.",
        current_cluster_name
      )
    )
    self.current_cluster_name = current_cluster_name
