import abc
import copy

import ioc
import yaml

from qsa.lib.serializers import SerializedDatastructure
from qsa.lib.serializers import DoubleQuotedString
from qsa.lib.datastructures import DTO
from qsa.lib.datastructures import ImmutableDTO


class Resource(abc.ABC):
    """The base class for all Kubernetes resources."""
    kind = abc.abstractproperty()
    api_version = abc.abstractproperty()
    stage = abc.abstractproperty()
    group = abc.abstractproperty()
    cluster_wide = False
    default_labels = {}
    defaults = {}
    prefix = '{{ K8S_NAMESPACE_PREFIX }}'

    @property
    def annotations(self):
        return self.metadata.setdefault('annotations', DTO())

    @property
    def labels(self):
        return self.metadata.setdefault('labels', DTO())

    @property
    def tags(self):
        return self._manifest.__ansible__.setdefault('tags', [])

    @tags.setter
    def tags(self, value):
        self._manifest.__ansible__.tags = value

    @property
    def metadata(self):
        return self._manifest.metadata

    @property
    def base_name(self):
        return str.replace(self.name, self.prefix, '')

    @property
    def base_qualname(self):
        return str.replace(self.qualname, self.prefix, '')

    @property
    def name(self):
        return self.metadata.name

    @name.setter
    def name(self, value):
        self.metadata.name = DoubleQuotedString(value)

    @property
    def namespace(self):
        return self.metadata.namespace

    @namespace.setter
    def namespace(self, value):
        self.metadata.namespace = value

    @property
    def qualname(self):
        return f'{self.namespace}.{self.name}'

    @classmethod
    def empty(cls, name, state='present', namespace=None, title=None, environments=None, initial=None):
        """Instantiate a new :class:`Kubernetes` resource with a
        skeleton.

        Args:
            manifest (qsa.lib.datastructures.DTO): a datastructure holding
                the resource manifest.
            name (str): a name for the resource.
            namespace (str): the namespace to contain the resource.
            state (str): specifies the state of this resource. Defaults
                to ``present``. Valid values are ``present``, ``absent``.
            title (str): specifies the title of the deployment task.
            environments (list): specify the environment to which this resource
                is deployed.

        Returns:
            Resource
        """
        manifest = DTO.fromdict({
            'apiVersion': cls.api_version,
            'kind': cls.kind,
            'metadata': {'name': DoubleQuotedString(name)},
            '__ansible__': {
                'name': title,
                'state': state,
                'new': True,
                'vars': {
                    'environments': []
                }
            }
        })
        manifest.update(DTO.fromdict(copy.deepcopy(cls.defaults)))
        if initial:
            manifest.update(initial)
        if not cls.cluster_wide:
            if namespace is None:
                raise TypeError("The `namespace` argument is required.")
            manifest.metadata.namespace = namespace
        resource = cls(manifest)
        if not cls.cluster_wide:
            resource.label('env', '{{ K8S_DEPLOYMENT_ENV }}',
                'deployment.quantumframework.org')
        resource.setdefaultlabels()
        resource.tag(f'k8s.quantumframework.org/task:{cls.stage}.{cls.group}')
        if cls.cluster_wide:
            resource.setunbound(True)
        return resource

    def __init__(self, manifest):
        """Initialize a new :class:`Resource`.

        Args:
            manifest (qsa.lib.datastructures.DTO): a datastructure holding
                the resource manifest.
        """
        self._manifest = manifest

    def annotate(self, name, value, domain=None):
        """Adds an annotations to the :class:`Resource`."""
        assert domain is not None
        self.annotations[f'{domain}/{name}'] = value
        return self

    def getmanifest(self):
        """Return a **new** dictionary containing the manifest."""
        # FIXME: Ensure that all annotations are dumped correctly.
        for k in self.annotations.keys():
            if '\n' not in self.annotations[k]:
                continue
            if isinstance(self.annotations[k], SerializedDatastructure):
                continue
            self.annotations[k] = SerializedDatastructure(self.annotations[k])
        return DTO.fromdict(self._manifest)

    def getresource(self):
        """Return a new dictionary representing the Kubernetes API
        resource definition.
        """
        resource = copy.deepcopy(self.getmanifest())
        if '__ansible__' in resource:
            resource.pop('__ansible__')
        return resource

    def dump(self):
        """Dumps the :class:`Resource` to a Python dictionary."""
        return ImmutableDTO.fromdict(self._manifest)

    def isnew(self):
        """Return a boolean indicating if the object is a new
        object.
        """
        return bool(self._manifest.__ansible__.get('new'))

    def isunbound(self):
        """Return a boolean if the :class:`Resource` is not bound to
        a specific environment within the cluster.
        """
        return self.labels.get('deployment.quantumframework.org/unbound') == 'true'

    def label(self, name, value, domain=None):
        """Adds a label to the :class:`Resource`."""
        value = DoubleQuotedString(value)
        if domain:
            self.labels[f'{domain}/{name}'] = value
        else:
            self.labels[name] = value

        # FIXME: this belongs somewhere else.
        if domain == 'app.kubernetes.io':
            if name == 'part-of':
                self.tag(f'app.kubernetes.io/part-of:{value}')

        return self

    def setdefaultlabels(self):
        """Sets the default labels for this :class:`Resource`."""
        self.labels.update(copy.deepcopy(self.default_labels))

    def setdefinition(self, definition):
        """Overwrite the current definition with the given datastructure."""
        self._manifest.update(definition)

    def setapplabels(self, name, part_of=None):
        """Sets the recommended Kubernetes labels."""
        self.label('name', name, 'app.kubernetes.io')
        if part_of:
            self.label('part-of', part_of, 'app.kubernetes.io')

    def setnamespace(self, namespace):
        """Override the namespace of the resource."""
        self.metadata.namespace = namespace
        return self

    def setunbound(self, enable=True):
        """Flag the :class:`Resource` as unbound."""
        tag = 'deployment.quantumframework.org/env:global'
        if enable:
            self.label('unbound', 'true',
                'deployment.quantumframework.org')
            self._manifest.__ansible__.vars['environments'] = ['cluster']
        else:
            self.label('unbound', 'false',
                'deployment.quantumframework.org')
            if 'cluster' in self._manifest.__ansible__.vars['environments']:
                self._manifest.__ansible__.vars['environments'].remove('cluster')
            self.on_bound()

        return self

    def settags(self, tags):
        self._manifest.__ansible__.tags = tags

    def setansibleprefix(self, name):
        """Set the prefixes used by Ansible to indicate the
        deployment environment to the given string `name`.
        """
        return f'{self.prefix}{name}'

    def settitle(self, title):
        """Sets the title for the deployment task of this resource."""
        self._manifest.__ansible__.name = str.format(title, res=self)

    def setcomponent(self, name):
        """Sets the component name."""
        self.label('component', name, 'app.kubernetes.io/component')

    def setenvironments(self, environments, annotate=True):
        """Sets the environments for this :class:`Resource`."""
        self._manifest.__ansible__.vars['environments'] = [x.name for x in environments]
        self.setunbound(not bool(environments))
        return self

    def setpartof(self, part_of):
        self.tag(f'app.kubernetes.io/part-of:{part_of}')
        self.labels['app.kubernetes.io/part-of'] = part_of

    def tag(self, name):
        if name not in self.tags:
            self.tags.append(name)

    def on_bound(self):
        """Executed when the resource is marked as bound."""
        if not self.cluster_wide:
            self.namespace  = f'{self.prefix}{self.namespace}'
