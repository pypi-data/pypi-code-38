from qsa.lib.datastructures import DTO
from .abstractrolebinding import AbstractRoleBinding
from .base import Resource
from .batch import ResourceBatch
from .certificate import Certificate
from .crd import CustomResourceDefinition
from .clusterissuer import AcmeClusterIssuer
from .clusterissuer import ClusterIssuer
from .clusterrole import ClusterRole
from .clusterrolebinding import ClusterRoleBinding
from .deployment import Deployment
from .namespace import Namespace
from .networkpolicy import NetworkPolicy
from .persistable import Persistable
from .prefixable import Prefixable
from .podsecuritypolicy import PodSecurityPolicy
from .serviceaccount import ServiceAccount
from .service import LoadBalancer
from .service import NodePort
from .service import Service


class Ingress(Resource, Persistable, Prefixable):
    kind = 'Ingress'
    api_version = 'extensions/v1beta1'
    group = 'ingress'
    stage = 'network'

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO())

    def setcaissuer(self, name):
        """Specifies the default ``ClusterIssuer`` for the ``Ingress``;
        use in combination with ``cert-manager``.
        """
        self.annotate('cluster-issuer', name,
            'certmanager.k8s.io')

    def setloadbalancer(self, name):
        """Sets the load balancer that provides incoming traffic to the
        ``Ingress``. Use with ``ingress-nginx``.
        """
        self.annotate('ingress.class', name,
            'kubernetes.io')


class ConfigMap(Resource, Persistable, Prefixable):
    kind = 'ConfigMap'
    api_version = 'v1'
    group = 'config'
    stage = 'config'

    @property
    def data(self):
        return self._manifest.setdefault('data', {})

    def setdata(self, data):
        """Sets the keys/values of the ``ConfigMap`` using the dictionary `data`."""
        self.data.update(data)


class Role(Resource, Persistable, Prefixable):
    kind = 'Role'
    api_version = 'rbac.authorization.k8s.io/v1'
    group = 'rbac'
    stage = 'iam'

    @property
    def rules(self):
        return self._manifest.rules

    def addrule(self, groups, resources, verbs, names=None):
        self.rules.append({
            'apiGroups': groups,
            'resources': resources,
            'verbs': verbs
        })
        if names:
            self.rules[-1]['resourceNames'] = names


class RoleBinding(Resource, AbstractRoleBinding, Persistable, Prefixable):
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'RoleBinding'
    group = 'rbac'
    stage = 'iam'

    @property
    def roleref(self):
        return self._manifest.setdefault('roleRef', {
            'apiGroup': 'rbac.authorization.k8s.io',
            'kind': 'Role'
        })


resource_types = {
    'Certificate'   : Certificate,
    'ClusterIssuer' : ClusterIssuer,
    'ClusterRole'   : ClusterRole,
    'ClusterRoleBinding': ClusterRoleBinding,
    'ConfigMap': ConfigMap,
    'CustomResourceDefinition'  : CustomResourceDefinition,
    'Deployment'    : Deployment,
    'LoadBalancer'  : LoadBalancer,
    'Namespace'     : Namespace,
    'NetworkPolicy' : NetworkPolicy,
    'NodePort'      : NodePort,
    'Role'          : Role,
    'RoleBinding'   : RoleBinding,
    'ServiceAccount': ServiceAccount
}


get_resource = resource_types.get
