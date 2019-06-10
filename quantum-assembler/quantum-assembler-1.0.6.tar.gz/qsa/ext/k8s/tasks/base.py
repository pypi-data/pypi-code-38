from qsa.lib.datastructures import DTO
from qsa.ext.ansible.model import Task


class KubernetesTask(Task):
    api_version = None
    kind = None
    module = 'k8s'
    annotation_domain = None
    label_domain = None
    prefix_env = "{{ K8S_NAMESPACE_PREFIX }}"
    with_prefix = False
    cluster_wide = False

    @property
    def annotations(self):
        return self.definition.metadata.setdefault('annotations', {})

    @property
    def labels(self):
        return self.definition.metadata.setdefault('labels', DTO.fromdict({
            'app.kubernetes.io/managed-by': 'qsa-cli'
        }))

    @property
    def qualname(self):
        name = f'{self.definition.metadata.namespace}-{self.definition.metadata.name}'\
            if not self.cluster_wide else self.definition.metadata.name
        return f'{self.ansible_ns}.{name}'

    @property
    def metadata(self):
        return self.definition.metadata

    @property
    def definition(self):
        return self.task.k8s.setdefault('definition', DTO())

    @property
    def tags(self):
        return self.task.setdefault('tags', [])

    @staticmethod
    def cleanvalue(value):
        return re.sub('[^\w\s-]', '-', value)\
            .lower()\
            .strip()

    @classmethod
    def load(cls, repository, task):
        return cls(repository, task)

    @classmethod
    def fromresource(cls, repository, resource, name, tags=None, force_playbook=None):
        task = DTO.fromdict({
            'name': name,
            'tags': tags or [],
            'k8s': {
                'definition': resource,
                'state': 'present'
            }
        })
        return cls(repository, task)

    def __init__(self, repository, task, _created=False):
        assert self.api_version
        assert self.kind
        self._created = _created
        self.repository = repository
        self.task = task
        t = f'kubernetes.io/resource-type:{self.kind.lower()}'
        if t not in self.tags:
            self.tag(t)

    def prefix(self, name):
        """Prefixes `name` with the Ansible environment key."""
        return f'{self.prefix_env}{name}'

    def setresourcename(self, name, part_of=None):
        """Sets the name of the resource."""
        self.definition.metadata.name = name
        self.label('name', name, 'app.kubernetes.io')
        self.labels["app"] = name
        if part_of:
            self.label('part-of', part_of, 'app.kubernetes.io')

    def tag(self, name):
        """Tag the :class:`KubernetesTask`."""
        # Remove the prefix_env from the name.
        if self.prefix_env in name:
            name = str.replace(name, self.prefix_env, '')
        if name not in self.tags:
            self.tags.append(name)

    def predump(self):
        if self.with_prefix:
            self.setenvprefix()

    def dump(self, *args, **kwargs):
        self.tag(f'ansible.quantumframework.org/namespace:{self.ansible_ns}')
        self.tag(f'ansible.quantumframework.org/task-impl:{self.classname}')
        self.tag(f'ansible.quantumframework.org/qualname:{self.qualname}')
        self.tag(f'meta.quantumframework.org/version:1.0')
        self.label('managed-by', 'qsa-cli', 'app.kubernetes.io')
        self.label('name', self.metadata.name, 'app.kubernetes.io')
        self.task.k8s.definition.update({
            'kind': self.kind,
            'apiVersion': self.api_version
        })
        self.task.tags = list(sorted(set(self.tags)))
        return self.task

    def setmessage(self, msg):
        self.task.name = msg

    def setresourcename(self, name, part_of=None):
        """sets the name of the deployment."""
        self.definition.metadata.name = name
        self.label('name', name, "app.kubernetes.io")
        if part_of:
            self.label('part-of', part_of, "app.kubernetes.io")

    def annotate(self, key, value, domain=None):
        """Annotate the resource."""
        if domain is None and not self.annotation_domain:
            raise ValueError("No annotation domain specified.")
        domain = domain or self.annotation_domain
        self.annotations[f"{domain}/{key}"] = value
        return self

    def label(self, key, value, domain=None):
        """Label the resource."""
        if domain is None and not self.label_domain:
            raise ValueError("No label domain specified.")
        domain = domain or self.label_domain
        self.labels[f"{domain}/{key}"] = value
        return self

    def setenvprefix(self, enable=True):
        """Sets the environment prefix to the relevant fields in
        the resource.
        """
        # Never prefix unbound resources
        if self.isunbound():
            return

        assert self.definition.metadata.namespace
        if enable:
            self.definition.metadata.namespace = f"{self.prefix_env}{self.namespace}"
        else:
            self.definition.metadata.namespace = str.replace(
                self.definition.metadata.namespace, self.prefix_env, '')

    def setnamespace(self, name):
        """Sets the namespace for the resource."""
        self.definition.metadata.namespace = name
        return self

    def setunbound(self, value=True):
        """Flag the resource as not bound to a specific environment."""
        self.tag('deployment.quantumframework.org/env:global')
        return self

    def persist(self):
        """Persists the task to disk."""
        self.repository.persist(self)

    @staticmethod
    def parsenamedport(value):
        """Parse a named port from the format `<name>:<src>:<dst>`."""
        # This would look better in a class.
        if value.count(':') == 1:
            name, src = str.split(value, ':')
            dst = None
            protocol_port = src
        elif value.count(':') == 2:
            name, src, dst = str.split(value, ':')
            protocol_port = dst
        else:
            raise ValueError(f"Invalid port format: {value}")
        protocol = 'TCP'
        if '/' in protocol_port:
            protocol = str.upper(str.split(protocol_port, '/')[-1])
        return DTO(name=name, src=int(src.split('/')[0]),
            dst=int(dst.split('/')[0]) if dst else None, protocol=protocol)
