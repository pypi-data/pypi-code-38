import six

from orchestrate.common import safe_format
from orchestrate.core.cluster.errors import ClusterError


class DisconnectOnException(object):
  def __init__(self, cluster_name, services):
    self._cluster_name = cluster_name
    self._services = services

  def __enter__(self):
    pass

  def __exit__(self, t, v, tb):
    if v is not None:
      try:
        self._services.cluster_service.disconnect(cluster_name=self._cluster_name, disconnect_all=False)
        instructions = safe_format(
          "You are now disconnected from cluster {cluster_name},"
          " please resolve the issue and re-run your command.",
          cluster_name=self._cluster_name
        )
      except Exception:
        instructions = safe_format(
          "Additionally, an error occured while attempting to disconnect from cluster {cluster_name}."
          " Please attempt to run `sigopt cluster disconnect -n {cluster_name}` before re-running any commands.",
          cluster_name=self._cluster_name
        )

      six.raise_from(
        ClusterError(safe_format(
          "An error occured: {}\n{}",
          str(v),
          instructions,
        )),
        v,
      )
    return True
