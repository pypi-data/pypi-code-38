from qsa.lib.datastructures import DTO
from qsa.lib.serializers import DoubleQuotedString
from .base import Resource
from .host import HostMixin
from .prefixable import Prefixable
from .persistable import Persistable


class Service(Resource, Prefixable, Persistable, HostMixin):
    api_version = 'v1'
    kind = 'Service'
    group = 'services'
    stage = 'network'

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO())

    @property
    def selector(self):
        return self.spec.setdefault('selector', DTO())

    @property
    def ports(self):
        return self.spec.setdefault('ports', [])

    def setselector(self, key, value):
        """Sets the selector for the ``Service``."""
        self.selector[key] = value
        return self

    def setportsfromstring(self, ports):
        """Expose ports of the service from a list of strings."""
        for port in ports:
            self.setportfromstring(port)
        return self

    def setportfromstring(self, value):
        """Parse a named port definition and expose it on the
        service.
        """
        self.setport(**self.parsenamedport(value))
        return self

    def setport(self, name, src, dst=None, protocol='TCP'):
        """Expose a port on the service."""
        spec = DTO.fromdict({
            'name': name,
            'port': src,
            'protocol': protocol
        })
        if dst:
            spec.targetPort = dst
        self.ports.append(spec)
        return self


class NodePort(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec.type = 'NodePort'


class LoadBalancer(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec.type = 'LoadBalancer'

    def setexternaltrafficpolicy(self, policy):
        """Sets the external traffic policy for the load balancer, if the
        vendor supports it.
        """
        self.spec.externalTrafficPolicy = policy
        return self

    def setloadbalancerip(self, ip):
        """Sets the external IP of the load balancer."""
        self.spec.loadBalancerIP = DoubleQuotedString(ip)
        return self

    def setsourceranges(self, ranges):
        """Sets the given list of CIDR's as allowed source
        ranges.
        """
        self.spec.loadBalancerSourceRanges = ranges
        return self
