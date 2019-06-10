from .clusterwide import ClusterWideResource
from .prefixable import Prefixable
from .persistable import Persistable


class ClusterRole(ClusterWideResource, Prefixable, Persistable):
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'ClusterRole'
    group = 'iam'
    stage = 'cluster'
