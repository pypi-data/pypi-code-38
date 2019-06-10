import copy
import itertools
import re

from qsa.lib.datastructures import DTO
from qsa.ext.ansible.model import Task
from .base import KubernetesTask
from .namespace import KubernetesNamespaceTask


class KubernetesTaskFactory:

    def __init__(self, repository):
        self.repository = repository

    def new(self, cls, name, namespace=None, *args, **kwargs):
        """Create a new Ansible task that modifies a Kubernetes
        cluster.
        """
        if not cls.cluster_wide and namespace is None:
            raise ValueError("Specify a namespace.")
        spec = DTO.fromdict({
            'name': kwargs.pop('message', f"create {cls.kind} '{name}'"),
            'tags': [],
            'k8s': {
                'state': 'present',
                'definition': {
                    'metadata': {'name': name}
                },
            }
        })
        if namespace:
            spec.k8s.definition.metadata.namespace = namespace
        task = cls(self.repository, spec, _created=True)
        return task


class ServiceTask(KubernetesTask):
    """Provisions a ``Service``."""
    ansible_ns = 'k8s.services'
    api_version = 'v1'
    kind = 'Service'
    setservicename = KubernetesTask.setresourcename

    @property
    def spec(self):
        return self.definition.setdefault('spec', DTO())

    @property
    def selector(self):
        return self.spec.setdefault('selector', DTO())

    @property
    def ports(self):
        return self.spec.setdefault('ports', [])

    def setselector(self, label, value):
        """Set a selector to which the service will load balance
        traffic.
        """
        self.selector[label] = value
        return self

    def setportsfromstring(self, values):
        """Parse a list of named port definitions and expose them
        on the service.
        """
        for port in values:
            self.setportfromstring(port)
        return self

    def setportfromstring(self, value):
        """Parse a named port definition and expose it on the
        service.
        """
        self.setport(**KubernetesTask.parsenamedport(value))

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


class LoadBalancerTask(ServiceTask):
    ansible_ns = 'k8s.loadbalancers'

    @property
    def ranges(self):
        return self.spec.loadBalancerSourceRanges

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec.type = 'LoadBalancer'

    def setloadbalancerip(self, ip):
        """Sets the external IP of the load balancer."""
        self.spec.loadBalancerIP = ip
        return self

    def setsourceranges(self, ranges):
        """Sets the given list of CIDR's as allowed source
        ranges.
        """
        self.spec.loadBalancerSourceRanges = ranges
        return self

    def addsourcerange(self, cidr):
        """Adds a source range to the load balancer that is
        allowed to connect.
        """
        if cidr not in self.ranges:
            self.ranges.append(cidr)


class BaseNamedSequence:

    @staticmethod
    def update(func):
        def decorator(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update()
            return result
        return decorator

    def __init__(self, task, spec):
        self.task = task
        self.spec = spec
        self.__index = {}

    def exists(self, name):
        """Return a boolean if the given volume exists."""
        return name in self.__index

    def _update(self):
        for i, volume in enumerate(self.spec):
            self.__index[volume.name] = volume


class Volumes(BaseNamedSequence):

    @BaseNamedSequence.update
    def addsecret(self, volume, name):
        """Mounts a secret from a volume."""
        self.spec.append(DTO.fromdict({
            'name': volume,
            'secret': {
                'secretName': name
            }
        }))



class Containers(BaseNamedSequence):

    def add(self, name, image):
        """Add a new container to the template."""
        if self.exists(name):
            raise Exception(f"A container named '{name}' already exists.")
        spec = DTO(name=name,
            image=f'{image}:latest',
            imagePullPolicy='Always'
        )
        self.spec.append(spec)
        return Container(self.task, spec)

    def get(self, name):
        for container in self.spec:
            if container.name != name:
                continue
            break
        else:
            raise LookupError(f"No such container: {name}")
        return Container(self.task, container)


class Container:

    @property
    def ports(self):
        return self.spec.setdefault('ports', [])

    @property
    def env(self):
        return self.spec.setdefault('env', [])

    @property
    def env_from(self):
        return self.spec.setdefault('envFrom', [])

    @property
    def mounts(self):
        return self.spec.setdefault('volumeMounts', [])

    def __init__(self, task, spec):
        self.task = task
        self.spec = spec

    def exposefromstring(self, port):
        """Expose a port on the container from a string spec."""
        protocol = 'TCP'
        name, port = str.split(port, ':')
        if '/' in port:
            port, protocol = str.split(str.upper(port), '/')
        assert port.isdigit()
        port = int(port)
        return self.expose(name, port, protocol)

    def expose(self, name, port, protocol):
        """Expose a port on the container."""
        self.ports.append(DTO(
            containerPort=port,
            name=name,
            protocol=protocol
        ))

    def setargs(self, args):
        """Sets the runtime arguments for the container."""
        self.spec.args = args

    def setenv(self, key, value):
        """Set an environment variable in the container."""
        self.env.append(DTO.fromdict({
            'name': key,
            'value': value
        }))

    def setenvfromconfigmap(self, name):
        """Populate the container environment from a ``ConfigMap``."""
        self.env_from.append(DTO.fromdict({
            'configMapRef': {
                'name': name
            }
        }))

    def setenvfromsecret(self, name):
        """Populate the container environment from a ``Secret``."""
        self.env_from.append(DTO.fromdict({
            'secretRef': {
                'name': name
            }
        }))

    def mountfromstring(self, value):
        """Mount a volume from a string specification."""
        volume, path, *mode = value.split(':')
        return self.mount(KubernetesTask.cleanvalue(volume), path,
            mode[0] if mode else None)

    def mount(self, name, path, mode=None):
        """Mount a volume at the given path."""
        self.mounts.append(DTO(
            name=name,
            mountPath=path,
            readOnly=mode=='ro'
        ))

    def persist(self, codebase):
        """Write the changes to the container to disk."""
        self.task.persist(codebase)


class DeploymentTask(KubernetesTask):
    """Provisions a Kubernetes deployment manifest."""
    ansible_ns = 'k8s.deployments'
    template_name = 'ci/ansible/task.k8s.deployment.yml.j2'
    api_version = 'apps/v1'
    kind = 'Deployment'

    @property
    def template(self):
        return self.definition.spec.setdefault('template', DTO())

    @property
    def spec(self):
        return self.definition.setdefault('spec', DTO())

    @property
    def strategy(self):
        return self.spec.setdefault('strategy', DTO())

    @property
    def containers(self):
        return Containers(self,
            self.template.spec.setdefault('containers', []))

    @property
    def volumes(self):
        return Volumes(self,
            self.template.spec.setdefault('volumes', []))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getdefaultspec(self):
        """Returns a default spec for this resource."""
        spec = super().getdefaultspec()
        spec.spec = DTO.fromdict({
            'template': {
                'metadata': {},
                'selector': {},
                'spec': {
                    'containers': []
                }
            }
        })
        return spec

    def addcontainer(self, name, image):
        """Adds a new container to the :class:`KubernetesDeploymentTask`."""
        return self.containers.add(name, image)

    def getcontainer(self, name):
        """Get a container instance by name."""
        return self.containers.get(name)

    def setautomounttoken(self, value):
        """Enable or disable the autmated mounting of the Kubernetes
        service account token.
        """
        self.template.spec.automountServiceAccountToken = value

    def setserviceaccount(self, name):
        """Sets the service account for the deployment."""
        self.template.spec.serviceAccountName = name

    def setdeploymentname(self, name, part_of=None):
        """sets the name of the deployment."""
        self.spec.metadata.name = name
        self.spec.metadata.labels["app.kubernetes.io/name"] = name
        self.spec.metadata.labels["app"] = name
        if part_of:
            self.spec.metadata.labels["app.kubernetes.io/part-of"] = part_of
        self.spec.spec.selector = DTO.fromdict({
            'matchLabels': {'app': name}
        })
        self.template.metadata.labels = DTO(app=name)

    def setrollingupdate(self, enable):
        """Enables or disables rolling update strategy."""
        if not enable and self.strategy.type == 'RollingUpdate':
            del self.template.spec.strategy

        if enable:
            self.strategy.type = 'RollingUpdate'
            self.strategy.maxUnavailable = 0
            self.strategy.maxSurge = 1

    def setmaxunavailable(self, n):
        """Sets the maximum number of unavailable replicas during
        update.
        """
        self.strategy.maxUnavailable = n

    def setmaxsurge(self, n):
        """Sets the maximum number of surging replicas during
        update.
        """
        self.strategy.maxSurge = n

    def setreplicas(self, n):
        """Sets the number of replicas."""
        self.spec.spec.replicas = n

    def setvolumefromsecretname(self, name):
        """Generate a name from a secret and create a volume
        for the pod.
        """
        volume = self.cleanvalue(name)
        if self.volumes.exists(volume):
            raise Exception(f"Volume {volume} exists.")
        self.volumes.addsecret(volume, name)

    def predump(self):
        """Enables the task if the spec is properly configured."""
        if self.spec.spec.template.spec and self.spec.metadata.name\
        and 'False' in self.conditions:
            self.conditions.remove('False')
        self.params.update({
            'state': self.state,
            'definition': self.spec
        })


class KubernetesConfigMapTask(KubernetesTask):
    ansible_ns = 'k8s.config'
    kind = 'ConfigMap'
    api_version = 'v1'

    def getdefaultspec(self):
        """Returns a default spec for this resource."""
        spec = super().getdefaultspec()
        spec.data = DTO()
        return spec


class CustomResourceDefinitionTask(KubernetesTask):
    ansible_ns = 'k8s.crd'
    kind = 'CustomResourceDefinition'
    api_version = 'apiextensions.k8s.io/v1beta1'
    cluster_wide = True


class RoleTask(KubernetesTask):
    ansible_ns = 'k8s.iam'
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'Role'
    cluster_wide = False

    @property
    def rules(self):
        return self.spec.setdefault('rules', [])

    def addrule(self, resources, verbs, groups, names=None):
        """Adds a permission to the :class:`RoleTask`. Does not
        update existing rules.
        """
        dto = DTO(resources=resources, verbs=verbs,
            apiGroups=groups)
        if names:
            dto.resourceNames = names
        self.rules.append(dto)


class RoleBindingTask(KubernetesTask):
    ansible_ns = 'k8s.rbac'
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'RoleBinding'
    cluster_wide = False

    @property
    def subjects(self):
        return self.definition.get('subjects', [])

    def getsubject(self, namespace, name):
        """Get a subject from the binding by its namespace and
        name.
        """
        for sub in self.subjects:
            if not (sub.name == name and sub.namespace == namespace):
                continue
            break
        else:
            raise LookupError(f"No such subject in namespace {namespace}: {subject}")
        return sub


class ClusterRoleTask(KubernetesTask):
    ansible_ns = 'k8s.cluster'
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'ClusterRole'
    cluster_wide = True


class ClusterRoleBindingTask(RoleBindingTask):
    ansible_ns = 'k8s.rbac'
    api_version = 'rbac.authorization.k8s.io/v1'
    kind = 'ClusterRoleBinding'
    cluster_wide = True


class APIServiceTask(KubernetesTask):
    ansible_ns = 'k8s.cluster'
    api_version = 'apiregistration.k8s.io/v1beta1'
    kind = 'APIService'
    cluster_wide = True


class ValidatingWebhookConfigurationTask(KubernetesTask):
    ansible_ns = 'k8s.cluster'
    api_version = 'admissionregistration.k8s.io/v1beta1'
    kind = 'ValidatingWebhookConfiguration'
    cluster_wide = True


class IssuerTask(KubernetesTask):
    ansible_ns = 'k8s.ca'
    api_version = 'certmanager.k8s.io/v1alpha1'
    kind = 'Issuer'
    cluster_wide = False


class CertificateTask(KubernetesTask):
    ansible_ns = 'k8s.pki'
    api_version = 'certmanager.k8s.io/v1alpha1'
    kind = 'Issuer'
    cluster_wide = False


class KubernetesServiceAccountTask(KubernetesTask):
    ansible_ns = 'k8s.iam'
    kind = 'ServiceAccount'
    api_version = 'v1'

    def setautomount(self, value):
        self.spec.automountServiceAccountToken = value

    def getdefaultspec(self):
        spec = super().getdefaultspec()
        spec.automountServiceAccountToken = False
        return spec


class KubernetesNetworkPolicyTask(KubernetesTask):
    ansible_ns = 'k8s.network'
    kind = 'NetworkPolicy'
    api_version = 'networking.k8s.io/v1'
    annotation_domain = "net.quantumframework.org"

    @property
    def spec(self):
        return self.definition.setdefault('spec', DTO())

    @property
    def egress(self):
        return self.spec.setdefault('egress', [])

    @property
    def ingress(self):
        return self.spec.setdefault('ingress', [])

    def allowegress(self, *args, **kwargs):
        return NetworkPolicy(self).allowegress(*args, **kwargs)

    def allowingress(self, *args, **kwargs):
        return NetworkPolicy(self).allowingress(*args, **kwargs)


class NetworkPolicy:

    @property
    def policy_types(self):
        return self.task.policy_types

    @property
    def egress(self):
        return self.task.egress

    @property
    def ingress(self):
        return self.task.ingress

    def __init__(self, task):
        self.task = task
        self.committed = False

    def allowingress(self, ports=None, protocols=None, namespace=None):
        """Creates an ingress rule for the :class:`NetworkPolicy`.

        Args:
            ports (list): destination ports that are allowed by
                this rule.
            protocols (list): protocols that are allowed by
                this rule. If no protocols are specified, TCP
                is assumed.
            namespace (string): the namespace to which this rule
                allows traffic.
        """
        protocols = protocols or ['TCP']
        rule = DTO()
        if 'Ingress' not in self.policy_types:
            self.policy_types.append('Ingress')
        for port, protocol in itertools.product(ports or [], protocols):
            rule.setdefault('ports', [])\
                .append({'port': port, 'protocol': protocol})

        if namespace:
            rule.setdefault('from', [])\
                .append({
                    'namespaceSelector': {
                        'matchLabels': {
                            f'{self.task.annotation_domain}/subnet': namespace
                        }
                    }
                })

        if rule:
            self.ingress.append(rule)
        return self

    def allowegress(self, ports=None, protocols=None, namespace=None):
        """Creates an egress rule for the :class:`NetworkPolicy`.

        Args:
            ports (list): destination ports that are allowed by
                this rule.
            protocols (list): protocols that are allowed by
                this rule. If no protocols are specified, TCP
                is assumed.
            namespace (string): the namespace to which this rule
                allows traffic.
        """
        protocols = protocols or ['TCP']
        rule = DTO()
        if 'Egress' not in self.policy_types:
            self.policy_types.append('Egress')
        for port, protocol in itertools.product(ports or [], protocols):
            rule.setdefault('ports', [])\
                .append({'port': port, 'protocol': protocol})

        if namespace:
            rule.setdefault('to', [])\
                .append({
                    'namespaceSelector': {
                        'matchLabels': {
                            f'{self.task.annotation_domain}/subnet': namespace
                        }
                    }
                })

        if rule:
            self.egress.append(rule)
        return self


CLASS_MAPPING = {
    'APIService'                        : APIServiceTask,
    'Certificate'                       : CertificateTask,
    'ClusterRole'                       : ClusterRoleTask,
    'ClusterRoleBinding'                : ClusterRoleBindingTask,
    'ConfigMap'                         : KubernetesConfigMapTask,
    'CustomResourceDefinition'          : CustomResourceDefinitionTask,
    'Deployment'                        : DeploymentTask,
    'Issuer'                            : IssuerTask,
    'Role'                              : RoleTask,
    'RoleBinding'                       : RoleBindingTask,
    'Namespace'                         : KubernetesNamespaceTask,
    'NetworkPolicy'                     : KubernetesNetworkPolicyTask,
    'Service'                           : ServiceTask,
    'ServiceAccount'                    : KubernetesServiceAccountTask,
    'ValidatingWebhookConfiguration'    : ValidatingWebhookConfigurationTask,
}



def fromdict(resource, task_name=None, nolabels=False, exclude=None, part_of=None,
    force_playbook=None, disable_firewall=False, force_namespace=None, only=None):
    """Create a new task from a dictionary with the proper
    labels and annotations.

    Args:
        name: specify a name for the tasks.
        resource: a dictionary with the resource definition.
        nolabels: do not add labels.
        exclude: a list of resources to exclude.
        force_playbook: force the resources to a specific
            playbook.
    """
    import ioc
    repository = ioc.require('ansible:TaskRepository')

    exclude = exclude or []
    if (resource.kind in exclude) or (only and resource.kind not in only):
        return
    ResourceTask = CLASS_MAPPING[resource.kind]
    name = resource.metadata.name
    task = ResourceTask.fromresource(repository, resource,
        name=task_name.format(kind=resource.kind) if name else None,
        force_playbook=force_playbook)
    task.setname(task_name.format(kind=resource.kind))
    if force_namespace is not None:
        task.setnamespace(force_namespace)
    if part_of:
        task.tag(f"app.kubernetes.io/part-of:{part_of}")
    return task
