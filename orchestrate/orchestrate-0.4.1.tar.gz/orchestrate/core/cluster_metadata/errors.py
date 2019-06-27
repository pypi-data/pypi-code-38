from orchestrate.common import safe_format
from orchestrate.core.exceptions import OrchestrateException


class MetadataError(OrchestrateException):
  def __init__(self, cluster_name, unformatted_msg):
    super(MetadataError, self).__init__(safe_format(
      '{msg} Disconnecting and then reconnecting should resolve the issue.',
      msg=safe_format(unformatted_msg, cluster_name=cluster_name),
    ))
    self.cluster_name = cluster_name


class MetadataNotFoundError(MetadataError):
  def __init__(self, cluster_name):
    super(MetadataNotFoundError, self).__init__(
      cluster_name,
      'We could not find metadata for cluster {cluster_name}.',
    )


class MetadataAlreadyExistsError(MetadataError):
  def __init__(self, cluster_name):
    super(MetadataAlreadyExistsError, self).__init__(
      cluster_name,
      'Looks like metadata for cluster {cluster_name} already exists.',
    )
