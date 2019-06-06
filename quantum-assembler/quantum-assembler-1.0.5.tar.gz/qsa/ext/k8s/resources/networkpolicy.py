import abc
import itertools

from qsa.lib.serializers import DoubleQuotedString
from qsa.lib.datastructures import DTO
from .base import Resource
from .prefixable import Prefixable
from .persistable import Persistable


class NetworkPolicy(Resource, Prefixable, Persistable):
    kind = 'NetworkPolicy'
    api_version = 'networking.k8s.io/v1'
    group = 'networkpolicies'
    stage = 'network'

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO(
            podSelector=DTO()
        ))

    @property
    def egress(self):
        return self.spec.setdefault('egress', [])

    @property
    def ingress(self):
        return self.spec.setdefault('ingress', [])

    @property
    def policy_types(self):
        return self.spec.setdefault('policyTypes', [])

    @policy_types.setter
    def policy_types(self, value):
        self.spec.policyTypes = value

    def allowegress(self, *args, **kwargs):
        return Rule(self).allowegress(*args, **kwargs)

    def allowingress(self, *args, **kwargs):
        return Rule(self).allowingress(*args, **kwargs)

    def allowinternaldns(self):
        """Allow DNS lookups."""
        self.allowegress(ports=[53], protocols=['UDP', 'TCP'])
        return self

    def addpolicytype(self, policy_type):
        """Adds a policy type to the ``policyTypes`` member."""
        if policy_type not in self.policy_types:
            self.policy_types.append(policy_type)
        return self

    def setpodselector(self, selector):
        self.spec.podSelector.matchLabels = selector
        return self

    def allownamespace(self):
        """Allow ingress and egress traffic from the same namespace."""
        self.policy_types = ['Ingress', 'Egress']
        self.spec.podSelector = DTO()
        self.allowingress(namespace=self.namespace)
        self.allowegress(namespace=self.namespace)
        return self

    def denyall(self):
        """Denies all traffic that is not matched by a rule that
        allows it.
        """
        self.spec.podSelector = DTO()
        self.policy_types = ['Ingress', 'Egress']
        return self

    def denyegress(self):
        """Deny all egress traffic."""
        self.spec.podSelector = DTO()
        if 'Egress' not in self.policy_types:
            self.policy_types.append('Egress')
        return self


class Rule(abc.ABC):

    def __init__(self, resource):
        self.resource = resource

    def allowingress(self, *args, **kwargs):
        return self.allow('Ingress', 'ingress', 'from', *args, **kwargs)

    def allowegress(self, *args, **kwargs):
        return self.allow('Egress', 'egress', 'to', *args, **kwargs)

    def allow(self, policy_type, key, direction, ports=None, protocols=None, namespace=None,
        cidr=None, tcp=None, pod=None):
        """Creates an  match criterion for the :class:`Rule`.

        Args:
            ports (list): destination ports that are allowed by
                this rule.
            protocols (list): protocols that are allowed by
                this rule. If no protocols are specified, TCP
                is assumed.
            namespace (string): the namespace to/from which this rule
                allows traffic.
            cidr (list): a list of CIDRs to allow traffic to.
            tcp (list): list of integers specifying allowed TCP ports.
        """
        protocols = protocols or ['TCP']
        policy = DTO()
        self.resource.addpolicytype(policy_type)
        for port, protocol in itertools.product(list(ports or []), protocols):
            policy.setdefault('ports', [])\
                .append({'port': port, 'protocol': protocol})

        for port in (tcp or []):
            policy.setdefault('ports', [])\
                .append({'port': port, 'protocol': 'TCP'})

        rules = policy.setdefault(direction, [])
        rule = {}
        if namespace:
            rule.update({
                'namespaceSelector': {
                    'matchLabels': {
                        f'app.kubernetes.io/name': DoubleQuotedString(namespace)
                    }
                }
            })

        if pod:
            rule.update({
                'podSelector': {
                    'matchLabels': pod
                }
            })

        if cidr:
            rule.update({
                'ipBlock': {
                    'cidr': DoubleQuotedString(cidr)
                }
            })

        if rule:
            rules.append(rule)
        else:
            # If the directional key is empty, remove it so that Kubernetes doesn't
            # see it as a change every time we update the resource state.
            policy.pop(direction)

        # If there is no namespace and and no pods, then all
        # traffic is allowed.
        if not namespace and not ports and not protocols:
            policy.podSelector = DTO()
        self.addtopolicy(key, policy)
        return self

    def addtopolicy(self, key, rule):
        getattr(self.resource, key).append(rule)
