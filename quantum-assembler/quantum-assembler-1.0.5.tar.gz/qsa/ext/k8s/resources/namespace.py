import yaml

from qsa.lib.datastructures import DTO
from .clusterwide import ClusterWideResource
from .prefixable import Prefixable
from .persistable import Persistable
from .networkpolicy import NetworkPolicy


class Namespace(ClusterWideResource, Prefixable, Persistable):
    """Represents a Kubernetes ``Namespace`` resource."""
    kind = 'Namespace'
    api_version = 'v1'
    group = 'namespaces'
    stage = 'meta'
    default_labels = {
        'net.quantumframework.org/isdmz': 'false'
    }

    @property
    def namespace(self):
        return self.name

    @property
    def subnet(self):
        """Returns the prefixed subnet name."""
        return f'{self.prefix}{self.base_name}'\
            if not self.isunbound()\
            else self.name

    def addpolicy(self, name):
        """Create a new :class:`NetworkPolicy` scoped to this
        :class:`Namespace`.
        """
        return self.create(NetworkPolicy, name)

    def create(self, cls, name, initial=None):
        """Create a new resource of the specified `cls` in this
        namespace.
        """
        resource = cls.empty(name, namespace=self.base_name, initial=initial)
        resource.setenvironments(self.getenvironments(), annotate=False)
        resource.label('name', name, 'app.kubernetes.io')
        return resource

    def getenvironments(self):
        """Get the environments in which this namespace is defined."""
        environments = yaml.safe_load(
            self.annotations['deployment.quantumframework.org/environments'])
        return [DTO(name=x) for x in environments]

    def setdefaultlabels(self):
        super().setdefaultlabels()
        self.label('subnet', self.subnet,
            'net.quantumframework.org')

    def setdmz(self, enable):
        """Flags the :class:`Namespace` as a DMZ."""
        if enable:
            self.label('isdmz', 'true', 'net.quantumframework.org')
        else:
            self.label('isdmz', 'false', 'net.quantumframework.org')

    def isdmz(self):
        """Return a boolean indicating if the namespace is a DMZ e.g.
        allowing ingress traffic from outside the Kubernetes cluster.
        """
        return self.labels.get('net.quantumframework.org/isdmz') == 'true'

    def on_persist(self, repo):
        self.label('subnet', self.subnet,
            'net.quantumframework.org')

    def on_bound(self):
        """Executed when the resource is marked as bound."""
        self.name  = f'{self.prefix}{self.base_name}'
        self.label('name', self.name,
            'app.kubernetes.io')

    def getenvname(self, env):
        """Return the name of the namespace in the given environment."""
        prefix = f'ns{env.alias}'
        return str.replace(self.qualname, self.prefix, prefix)

    def getresourcenamespace(self, namespace):
        """Return the resource namespace."""
        if not self.isunbound() and not str.startswith(namespace, self.prefix):
            namespace = f'{self.prefix}{namespace}'
        return namespace
