from .abstractrolebinding import AbstractRoleBinding
from .clusterwide import ClusterWideResource
from .prefixable import Prefixable
from .persistable import Persistable


class ClusterRoleBinding(AbstractRoleBinding, ClusterWideResource, Prefixable, Persistable):
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'ClusterRoleBinding'
    group = 'iam'
    stage = 'security'

    @property
    def roleref(self):
        return self._manifest.setdefault('roleRef', {
            'apiGroup': 'rbac.authorization.k8s.io',
            'kind': 'ClusterRole'
        })
