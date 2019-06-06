import base64
import copy
import itertools

import yaml
from ansible.plugins.filter.core import b64encode
from ansible.plugins.filter.core import b64decode

from qsa.lib.datastructures import DTO
from qsa.lib.datastructures import ImmutableDTO
from qsa.lib.serializers import Base64DER


class Secret:
    raw_types = [
        'secrets.quantumframework.org/gcloud/serviceaccount',
    ]
    b64_encoded_types = [
        'secrets.quantumframework.org/gcloud/serviceaccount:serviceaccount.p12',
        'secrets.quantumframework.org/gcloud/serviceaccount:serviceaccount.json',
    ]

    @property
    def base64(self):
        data = {}
        for key in self.data:
            value = self.data[key]
            if value.startswith('-----'):
                # TODO: A very ugly hack to properly dump
                # SSH keys.
                value = Base64DER(str(value))
            if f'{self.kind}:{key}' in self.b64_encoded_types:
                value = b64decode(value)
            data[key] = b64encode(value)
        return data

    def encode(self, dto, encode=True):
        data = {}
        b64encode = b64encode if encode else (lambda x: x)
        for key in dto:
            value = dto[key]
            if value.startswith('-----'):
                # TODO: A very ugly hack to properly dump
                # SSH keys.
                value = Base64DER(str(value))
            if f'{self.kind}:{key}' in self.b64_encoded_types:
                value = b64decode(value)
            data[key] = b64encode(value)
        return data

    def __init__(self, kind, name, data, namespace=None, annotations=None, labels=None, string_data=None):
        self.kind = kind
        self.namespace = namespace or []
        self.name = name
        self.data = data or {}
        self.annotations = annotations or {}
        self.labels = labels or {}
        self.string_data = string_data or {}
        if self.namespace and isinstance(self.namespace, str):
            self.namespace = [self.namespace]

    def __str__(self):
        template = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': self.name
            },
            'type': 'Opaque',
            'data': self.base64,
            'stringData': self.encode(dict(self.string_data), encode=False)
        }
        result = ''
        if self.labels:
            template['metadata']['labels'] = dict(self.labels)
        if self.annotations:
            template['metadata']['annotations'] = dict(self.annotations)
        for i, ns in enumerate(self.namespace):
            if i > 0:
                result += '\n\n\n---\n'
            spec = copy.deepcopy(template)
            spec['metadata']['namespace'] = ns
            result += str.strip(
                yaml.safe_dump(spec, indent=2, default_flow_style=False))
        return result


class Cluster:

    @property
    def dmz(self):
        return DTO.fromdict(self.spec.dmz or {})

    @property
    def namespaces(self):
        return DTO.fromdict(self.spec.namespaces or {})

    def __init__(self, quantum, spec):
        self.quantum = quantum
        self.spec = spec

    def updatens(self, namespace):
        """Updates the global state with the namespace."""
        k = 'dmz' if namespace.isdmz() else 'namespaces'

    def getns(self, name):
        """Returns a :class:`Namespace` object, identified by `name`."""
        return Namespace(self.quantum, self, (self.dmz|self.namespaces)[name])


class NetworkPolicy:

    @property
    def policy_types(self):
        types = []
        if self.spec.type == 'ingress':
            types.append('Ingress')
        if self.spec.type == 'egress':
            types.append('Egress')
        if self.spec.type == 'ingress+egress':
            types.append('Ingress')
            types.append('Egress')
        return types

    def __init__(self, cluster, namespace, name, spec):
        self.cluster = cluster
        self.namespace = namespace
        self.name = name
        self.spec = spec

    def __str__(self):
        base_spec = DTO.fromdict({
            'apiVersion': "networking.k8s.io/v1",
            'kind': "NetworkPolicy",
            'metadata': {},
            'spec': {}
        })
        resources = []
        for env in self.namespace.environments:
            spec = copy.deepcopy(base_spec)
            spec.metadata.name = self.name
            spec.metadata.namespace = f'{env}-{self.namespace.name}'
            spec.spec.policyTypes = self.policy_types
            spec.spec.podSelector = DTO()
            spec.spec[self.spec.type] = []
            base_rule = DTO()
            base_selectors = base_rule['to' if self.spec.type == 'egress' else 'from'] = []
            if self.spec.get('pod'):
                spec.spec.podSelector = {
                    'matchLabels': {
                        'app.kubernetes.io/name': self.spec.pod
                    }
                }
            if self.spec.get('ports'):
                base_rule.ports = self.spec.ports

            # Create concrete implementations
            namespaces = self.spec.get('namespaces') or [None]
            ranges = self.spec.get('cidr') or [None]

            #if self.spec.get('namespace'):
            #    base_selectors.append({
            #        'namespaceSelector': {
            #            'matchLabels': {
            #                'networking.quantumframework.org/vlan': f'{env}-{self.spec.namespace}'
            #            }
            #        }
            #    })

            for ns, cidr in itertools.product(namespaces, ranges):
                rule = copy.deepcopy(base_rule)
                field = 'to' if self.spec.type == 'egress' else 'from'
                selectors = rule[field] =\
                    copy.deepcopy(base_selectors)
                if cidr is not None:
                    selectors.append({
                        'ipBlock': {'cidr': cidr}
                    })
                if ns is not None:
                    vlan = ns if self.spec.get('noprefix')\
                        else f'{env}-{ns}'
                    selectors.append({
                        'namespaceSelector': {
                            'matchLabels': {
                                'networking.quantumframework.org/vlan': vlan
                            }
                        }
                    })
                if not rule[field] and rule.get('ports'):
                    del rule[field]
                spec.spec[self.spec.type].append(rule)

            if self.spec.get('ingress'):
                spec.spec['ingress'] = []
                ports = self.spec.ingress.get('ports')
                ranges = self.spec.ingress.get('ranges') or [None]
                ns = None
                for cidr in ranges:
                    rule = {}
                    if ports:
                        rule['ports'] = ports
                    selectors = rule['from'] = []
                    if cidr is not None:
                        selectors.append({
                            'ipBlock': {'cidr': cidr}
                        })
                    if ns is not None:
                        vlan = ns if self.spec.get('noprefix')\
                            else f'{env}-{ns}'
                        selectors.append({
                            'namespaceSelector': {
                                'matchLabels': {
                                    'networking.quantumframework.org/vlan': vlan
                                }
                            }
                        })
                    spec.spec.policyTypes.append('Ingress')
                    spec.spec['ingress'].append(rule)

            resources.append(spec)

        return '\n\n---\n'.join([
            yaml.safe_dump(x, indent=2, default_flow_style=False)
            for x in resources])

class Namespace:

    @staticmethod
    def parse_ports(ports):
        parsed = []
        for p in ports:
            if '/' in p:
                port, protocol = p.split('/')
                parsed.append({
                    'port': int(port),
                    'protocol': str.upper(protocol)
                })
                continue
            parsed.append({
                'port': int(p),
                'protocol': 'TCP'
            })
        return parsed

    @property
    def name(self):
        return self.spec.name

    @property
    def policies(self):
        return [NetworkPolicy(self.cluster, self, name, spec)
            for name, spec in self.spec.rules.items()]

    @property
    def environments(self):
        for env in self.spec.environments:
            yield self.quantum.get(
                f'deployment.environments.{env}.alias', env)

    def __init__(self, quantum, cluster, spec):
        self.quantum = quantum
        self.cluster = cluster
        self.spec = spec

    def allowdst(self, name, cidr=None, namespaces=None, pod=None, ports=None, ingress=None, noprefix=False):
        """Allows egress traffic from the namespace to the
        specified destinations. Also create an ingress rule
        if a destination namespace is defined, except the
        target is a DMZ (allow all ingress traffic).
        """
        k = 'dmz' if self.isdmz() else 'namespaces'
        nsspec = self.quantum.get(f'k8s.cluster.{k}.{self.name}')
        nsspec.rules = rules = self.spec.get('rules') or {}
        rule = nsspec.rules[name] = {
            'type': 'egress'
        }
        if cidr:
            rule['cidr'] = cidr
        if namespaces:
            rule['namespaces'] = namespaces
        if pod:
            rule['pod'] = pod
        if ports:
            rule['ports'] = self.parse_ports(ports)
        if ingress.get('ports') or ingress.get('namespaces'):
            rule['ingress'] = ingress
            if ingress.get('ports'):
                rule['ingress']['ports'] = self.parse_ports(ingress.ports)
        if noprefix:
            rule['noprefix'] = True
        self.quantum.assembler.notify('spec_updated', self.quantum)

    def getlb(self):
        """Returns the loadbalancer for this namespace, if any."""
        return self.quantum.get(f'k8s.cluster.dmz.{self.name}.loadbalancer', None)

    def getallnames(self):
        """Return a list of the concrete namespaces that are being
        created.
        """
        results = []
        for env in self.spec.environments:
            alias = self.quantum.get(f'deployment.environments.{env}.alias', env)
            results.append(f'{alias}-{self.spec.name}')
        return results

    def isdmz(self):
        """Return a boolean indicating if the namespace is a DMZ."""
        return 'ingress' in self.spec

    def __str__(self):
        base_spec = DTO.fromdict({
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {}
        })
        namespaces = []
        if self.spec.annotations:
            base_spec.metadata.annotations = dict(self.spec.annotations)

        # Create a namespace in each declared environment.
        for env in self.spec.environments:
            a = DTO()
            l = DTO.fromdict({
                'app.kubernetes.io/managed-by': 'qsa-cli',
                'app.kubernetes.io/part-of': self.quantum.get('project.name')
            })

            ns = copy.deepcopy(base_spec)
            env = self.quantum.get(f'deployment.environments.{env}.alias', env)

            ns.metadata.name = subnet = name = f'{env}-{self.spec.name}'

            # Set the network (subnet) name from the name.
            l['networking.quantumframework.org/vlan'] = subnet
            if self.isdmz():
                a['networking.quantumframework.org/isdmz'] = "true"

            if a:
                ns.metadata.annotations = a
            if l:
                ns.metadata.labels = l
            namespaces.append(ns)

            # Create the default deny policy for the namespace.
            policy = {
                'apiVersion': "networking.k8s.io/v1",
                'kind': 'NetworkPolicy',
                'metadata': {
                    'name': "default-deny-all",
                    'namespace': name,
                    'labels': {
                        'app.kubernetes.io/managed-by': 'qsa-cli',
                        'app.kubernetes.io/part-of': self.quantum.get('project.name')
                    }
                },
                'spec': {
                    'podSelector': {},
                    'policyTypes': ['Egress']
                }
            }
            if self.isdmz():
                policy['metadata']['name'] = 'default-allow-all'
                policy['spec']['egress'] = [{}]
                policy['spec']['ingress'] = [{}]
                policy['spec']['policyTypes'].append('Ingress')
            if not self.isdmz():
                # Non-DMZ namespaces also deny all ingress traffic.
                policy['spec']['policyTypes'].append('Ingress')

                # All all pods in the network to connect to each other.
                policy['spec']['egress'] = [{
                    'to': [{
                        'namespaceSelector': {
                            'matchLabels': {
                                'networking.quantumframework.org/vlan': f'{name}'
                            }
                        }
                    }]
                }]
                policy['spec']['ingress'] = [{
                    'from': [{
                        'namespaceSelector': {
                            'matchLabels': {
                                'networking.quantumframework.org/vlan': f'{name}'
                            }
                        }
                    }]
                }]

                # Allow DNS traffic so that internal names may be queried.
                # Blocking outside DNS servers is assumed to be configured
                # at the physical/cloud network level.
                policy['spec']['egress'].append({
                    'ports': [{'port': 53, 'protocol': 'UDP'}, {'port': 53, 'protocol': 'TCP'}]
                })
            namespaces.append(policy)

        return '\n\n---\n'.join(
            [yaml.safe_dump(x, indent=2, default_flow_style=False)
                for x in namespaces]) + '\n\n'
