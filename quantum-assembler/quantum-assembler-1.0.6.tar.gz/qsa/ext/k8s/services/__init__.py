import itertools

import ioc
import requests
import yaml

from qsa.lib.datastructures import DTO
from qsa.ext.k8s import tasks
from qsa.ext.k8s.resources import *
from qsa.ext.k8s.resources import get_resource


class Conflict(Exception):
    pass


class ResourceCreateService:
    NamespaceExists = type('NamespaceExists', (Conflict,), {})
    resource_types = {
        'Certificate'               : Certificate,
        'AcmeClusterIssuer'         : AcmeClusterIssuer,
        'ClusterIssuer'             : ClusterIssuer,
        'ClusterRole'               : ClusterRole,
        'ClusterRoleBinding'        : ClusterRoleBinding,
        'ConfigMap'                 : ConfigMap,
        'CustomResourceDefinition'  : CustomResourceDefinition,
        'Deployment'                : Deployment,
        'LoadBalancer'              : LoadBalancer,
        'Namespace'                 : Namespace,
        'NetworkPolicy'             : NetworkPolicy,
        'NodePort'                  : NodePort,
        'Role'                      : Role,
        'RoleBinding'               : RoleBinding,
        'ServiceAccount'            : ServiceAccount
    }
    codebase = ioc.class_property('core:CodeRepository')
    repo = ioc.class_property('k8s:Repository')

    def __init__(self, quantum, project, ansible, codebase, deployment):
        self.quantum = quantum
        self.project = project
        self.ansible = ansible
        self.deployment = deployment

    def _get(self, resource_type, name, *args, **kwargs):
        part_of = kwargs.pop('part_of', None)
        resource = self.repo.get(self.resource_types[resource_type],
            name, *args, **kwargs)
        resource.tag(f'app.kubernetes.io/name:{name}')
        resource.label('name', name, 'app.kubernetes.io')
        if part_of:
            resource.setpartof(part_of)
        return resource

    def certificate(self, issuer, namespace, name, secret, cn=None, istls=False,
        part_of=None, acme=False):
        """Create a new ``Certificate`` resource."""
        ns = self.repo.get('Namespace', namespace)
        assert not ns.isnew()
        if cn is None:
            raise NotImplementedError
        crt = ns.create(get_resource('Certificate'), name)
        crt.setsecret(secret)
        crt.setissuer(*str.split(issuer, '/'))
        if cn:
            crt.setcn(cn, istls=istls)
        crt.label('name', name, 'app.kubernetes.io')
        crt.label('component', 'X.509', 'app.kubernetes.io')
        crt.tag(f'app.kubernetes.io/name:{name}')
        crt.setacme(acme)
        if part_of:
            crt.label('part-of', part_of, 'app.kubernetes.io')
        return crt

    def configmap(self, namespace, name, data=None):
        """Create a new ``ConfigMap`` resource."""
        ns = self.repo.get('Namespace', namespace)
        assert not ns.isnew()
        cfg = ns.create(get_resource('ConfigMap'), name)
        cfg.setdata(data or {})
        cfg.label('name', name, 'app.kubernetes.io')
        cfg.label('managed-by', 'qsa-cli', 'app.kubernetes.io')
        cfg.tag(f'app.kubernetes.io/name:{name}')
        return cfg

    def clusterissuer(self, name, secret, acme=False, email=None):
        """Create a new ``ClusterIssuer``."""
        issuer = self._get('ClusterIssuer' if not acme else 'AcmeClusterIssuer',
            name)
        issuer.setsecret(secret)
        if email is not None:
            issuer.setacmeemail(email)
        return issuer

    def clusterrolebinding(self, resource_name, role, namespace, service_account, **kwargs):
        """Create a new ``ClusterRoleBinding`` for the specified
        service account with the given role.
        """
        binding = self._get('ClusterRoleBinding', resource_name, **kwargs)
        binding.addsubject({
            'namespace': namespace,
            'name': service_account,
            'kind': 'ServiceAccount'
        })
        binding.setrole(role)
        return binding

    def nodeport(self, namespace, name, msg=None):
        """Creates a new ``Loadbalancer`` resource."""
        return self._get('NodePort', name, namespace=namespace,
            title=msg or f"created load balancer service '{name}'")

    def loadbalancer(self, namespace, name, msg=None):
        """Creates a new ``Loadbalancer`` resource."""
        return self._get('LoadBalancer', name, namespace=namespace,
            title=msg or f"created load balancer service '{name}'")

    def namespace(self, name, isdmz=False, environments=None, unbound=False, msg=None,
        labels=None, annotations=None, part_of=None):
        """Creates a new ``Namespace`` resource and configures the
        appropriate network policies.
        """
        ns = self._get('Namespace', name, title=msg or f"created namespace '{name}'",
            environments=environments)
        subnet = name
        if not ns.isnew():
            raise self.NamespaceExists(name)

        environments = environments or []
        for i, env in enumerate(environments):
            environments[i] = d = self.deployment.getenv(env)
            if d is None:
                raise ValueError(f"No such environment: {env}")

        ns.setapplabels(name, part_of=part_of or self.project.symbolic_name)
        if isdmz:
            ns.setdmz(True)

        if environments:
            ns.setenvironments(environments)
            assert not ns.isunbound()

        # If there are no environments, this namespace is considered
        # 'unbound' - e.g. not tied to any deployment environment.
        ns.setunbound(not bool(environments))

        # Handle labels and annotations
        if labels:
            for x, y in map(lambda x: str.split(x,'='), labels):
                domain, key = str.split(x, '/', 1)
                task.label(key, y, domain=domain)
        if annotations:
            for x, y in map(lambda x: str.split(x,'='), annotations):
                domain, key = str.split(x, '/', 1)
                task.annotate(key, y, domain=domain)

        self.repo.add(ns)

        allow = deny = None
        if not isdmz:
            # Create a network policy forbidding all traffic from outside
            # the namespace.
            deny = self.networkpolicy(subnet, 'default-deny',
                msg=f"created default deny network policy for namespace {name}",
                environments=environments)
            deny.denyall()
            allow = self.networkpolicy(subnet, 'default-allow',
                msg=f"created default allow network policy for namespace {name}",
                environments=environments)
            allow.allownamespace()
            allow.allowinternaldns()
        else:
            # Disallow most egress traffic and allow all ingress traffic.
            deny = self.networkpolicy(subnet, 'default-deny',
                msg=f"created default deny network policy for namespace {name}",
                environments=environments)
            deny.denyegress()\
                .allowingress()

            allow = self.networkpolicy(subnet, 'default-allow',
                msg=f"created default network policy for namespace {name}",
                environments=environments)
            allow.setpodselector({})
            allow.allowinternaldns()

        if allow:
            self.repo.add(allow)
        if deny:
            self.repo.add(deny)

        assert ns is not None
        return ns

    def networkpolicy(self, namespace, name, environments=None, msg=None, part_of=None):
        """Create a new ``NetworkPolicy`` resource."""
        environments = environments or []
        qualname = name
        msg = msg or f"created default network rules for namespace {name}"
        np = self._get('NetworkPolicy', qualname, namespace=namespace, title=msg)
        assert np.isnew(), np.dump()
        np.setapplabels(name, part_of=part_of or self.project.symbolic_name)
        np.setenvironments(environments or [])
        self.repo.add(np)
        return np

    def importresources(self, resources, name, part_of=None, force_playbook=None, exclude=None,
        tags=None, disable_firewall=False, force_namespace=None, only=None, environments=None):
        """Imports a set of resources."""
        playbooks = {}
        imported = []
        for resource in resources:
            if not resource:
                continue
            dto = DTO.fromdict(resource)
            kind = dto.kind
            if (only and kind not in only) or (exclude and kind in exclude):
                continue

            params = {'name': dto.metadata.name}
            if 'namespace' in dto.metadata:
                params['namespace'] = dto.metadata.namespace
            resource = self.resource_types[dto.kind].empty(**params)
            resource.setdefinition(dto)
            resource.setapplabels(dto.metadata.name, part_of)
            resource.setunbound(not bool(environments))
            if force_namespace:
                resource.setnamespace(force_namespace)
            if name:
                resource.settitle(name.format(kind=resource.kind))
            if tags:
                resource.settags(tags)

            if part_of:
                resource.tag(f'app.kubernetes.io/part-of:{part_of}')

            if force_playbook:
                resource.label('forced-group', force_playbook,
                    'ansible.quantumframework.org')
            self.repo.add(resource, stage=force_playbook)
            imported.append(resource)

        return ResourceBatch(imported)

    def importmanifest(self, uri, name, part_of=None, force_playbook=None, exclude=None,
        tags=None, disable_firewall=False, force_namespace=None, only=None, environments=None):
        """Imports a resource manifest from the specified URI."""
        response = requests.get(uri)
        response.raise_for_status()
        resources = yaml.safe_load_all(response.text)
        if environments:
            raise NotImplementedError

        playbooks = {}
        imported = []
        for resource in resources:
            if not resource:
                continue
            dto = DTO.fromdict(resource)
            kind = dto.kind
            if (only and kind not in only) or (exclude and kind in exclude):
                continue

            params = {'name': dto.metadata.name}
            if 'namespace' in dto.metadata:
                params['namespace'] = dto.metadata.namespace
            resource = self.resource_types[dto.kind].empty(**params)
            resource.setdefinition(dto)
            resource.setapplabels(dto.metadata.name, part_of)
            resource.setunbound(not bool(environments))
            if force_namespace:
                resource.setnamespace(force_namespace)
            if name:
                resource.settitle(name.format(kind=resource.kind))
            if tags:
                resource.settags(tags)

            if force_playbook:
                resource.label('forced-group', 'bootstrap',
                    'ansible.quantumframework.org')
            self.repo.add(resource, stage=force_playbook)
            imported.append(resource)

        return ResourceBatch(imported)

    def serviceaccount(self, namespace, name, automount=False):
        """Create a new ``ServiceAccount``."""
        ns = self.repo.get('Namespace', namespace)
        sa = ns.create(get_resource('ServiceAccount'), name)
        return sa
