import io
import re
import os
import glob

import ioc
import yaml

from qsa.lib.datastructures import DTO
from .const import TAG_DEPLOYMENT_ENV
from .const import TAG_DEPLOYMENT_GROUP
from .const import TAG_DEPLOYMENT_PHASE
from .resources import get_resource


class KubernetesRepository:
    """Provides an abstraction layer to the persistence of
    :class:`~qsa.ext.k8s.resource.base.Resource` objects.
    """
    base_path = 'ops/ansible/templates/k8s'
    padding = 4
    codebase = ioc.class_property('core:CodeRepository')

    def __init__(self, base_path=None):
        self.base_path = self.codebase.abspath(base_path or self.base_path)

    def get(self, cls, name, namespace=None, *args, **kwargs):
        """Loads a :class:`Persistable` from the persistent storage
        backend.
        """
        allow_create = kwargs.pop('allow_create', True)
        if isinstance(cls, str):
            cls = get_resource(cls)
        dirname, abspath, fn, new = self.get_storage_path(cls.stage,
            cls.getfilename(name, namespace=namespace))
        if new:
            if not allow_create:
                raise LookupError(name)
            resource = cls.empty(name, namespace=namespace, *args, **kwargs)
        else:
            resource = StoredManifest.asresource(cls, abspath)
        return resource

    def add(self, persistable, stage=None):
        """Adds the :class:`Persistable` to the repository."""
        dirname, abspath, fn, new = self.get_storage_path(
            stage or persistable.stage, persistable.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        persistable._on_persist(self, abspath, fn, new)
        self.codebase.write(abspath, persistable.render(fn, stage))

    def get_storage_path(self, stage, filename):
        """Returns the storage path at which the persistable must
        be written.
        """
        dirname = os.path.join(self.base_path, stage)

        # Either find the existing path or generate a new serial.
        files = []
        new = False
        for fn in sorted(glob.glob(f'{dirname}/*.yml')):
            serial, qualname = str.split(os.path.basename(fn), '-', 1)
            if filename != qualname:
                files.append(fn)
                continue
            src = fn
            fn = os.path.basename(fn)
            break
        else:
            new = True
            list.sort(files)
            if bool(files):
                serial, _ = str.split(os.path.basename(files[-1]), '-', 1)
                assert str.isdigit(serial), files[-1]
                serial = str(int(serial) + 1).zfill(self.padding)
            else:
                serial = ''.zfill(self.padding)
            fn = f'{serial}-{filename}'
            src = os.path.join(dirname, fn)
            assert not os.path.exists(src), src
        return dirname, src, fn, new


class StoredManifest:
    """Represents a manifest stored on disk."""
    pattern = re.compile('^#\sansible\:\s')

    @classmethod
    def asresource(cls, Resource, src):
        """Load the manifest from disk and parse its contents."""
        manifest = DTO()
        buf = ''
        for line in open(src).readlines():
            if not cls.pattern.match(line):
                continue
            buf += cls.pattern.sub('', line)
        task = DTO.fromdict(yaml.safe_load(buf))
        manifest.__ansible__ = DTO.fromdict({
            'name': task.name,
            'state': task.k8s.state,
            'new': False,
            'tags': task.tags,
            'when': task.when,
            'vars': task.vars
        })
        manifest.update(yaml.safe_load(open(src)))
        return Resource(DTO.fromdict(manifest))


class AnsibleHeader:
    """The header in a manifest template that contains the Ansible
    task definition.
    """
    pattern = re.compile('^#\sansible\:\s')

    @classmethod
    def parse(cls, src):
        manifest = DTO()
        buf = ''
        for line in open(src).readlines():
            if not cls.pattern.match(line):
                continue
            buf += cls.pattern.sub('', line)[1:]
        return cls(yaml.safe_load(buf))

    def __init__(self, spec):
        self.spec = DTO.fromdict(spec)

    def tag(self, tag):
        self.spec.tags.append(tag)
        self.spec.tags = list(sorted(set(self.spec.tags)))

    def untag(self, tag):
        if tag in self.spec.tags:
            self.spec.tags.remove(tag)
        self.spec.tags = list(sorted(set(self.spec.tags)))

    def setname(self, name):
        """Sets the Ansible task name."""
        self.spec.name = name

    def setsource(self, src):
        """Sets the source file for the Ansible task."""
        self.spec.loop = src

    def render(self):
        """Renders the header."""
        buf = ''
        for line in io.StringIO(self.yaml()).readlines():
            buf += f'# ansible: {line}'
        return buf

    def yaml(self):
        return yaml.safe_dump(self.spec, indent=2,
            default_flow_style=False)



class UnmanagedManifest(StoredManifest):
    stage = 'post'

    # The Ansible task is a loop because an imported manifest
    # may consist of multiple documents.

    @property
    def filename(self):
        assert self.name
        return self.getfilename(self.name)

    @classmethod
    def getfilename(cls, name, *args, **kwargs):
        assert name
        return f'{name}.yml'

    @classmethod
    def empty(cls, name, *args, **kwargs):
        return cls(name, AnsibleHeader({
            'k8s': {
                'state': 'present',
            },
            'loop': None,
            'tags': []
        }))

    def __init__(self, name, header):
        self.name = name
        self.header = header
        self.manifest = None
        self.header.tag(f'{TAG_DEPLOYMENT_GROUP}:manifests')
        self.header.tag(f'{TAG_DEPLOYMENT_PHASE}:post')

    def tag(self, tag):
        self.header.tag(tag)

    def setunbound(self, enable=True):
        """Mark the manifest as bound not to a specific deployment
        environment.
        """
        if enable:
            self.header.tag(f'{TAG_DEPLOYMENT_ENV}:global')
        else:
            self.header.untag(f'{TAG_DEPLOYMENT_ENV}:global')

    def setcontentfromfile(self, src):
        """Sets the contents of the :class:`UnmanagedManifest`
        from the file at `src`.
        """
        with open(src) as f:
            self.manifest = f.read()

    def setenvironments(self, environments):
        """Configures the manifest to deploy to the specified environments."""
        for name in environments:
            self.header.tag(f'{TAG_DEPLOYMENT_ENV}:{name}')

    def settaskname(self, name):
        """Sets the Ansible task name."""
        self.header.setname(name)

    def _on_persist(self, repo, dst, fn, new):
        # We now know the path from which the loop should
        # retrieve the base file.
        self.header.setsource(f'k8s/post/{fn}')

    def render(self, fn, stage):
        return '\n'.join([self.header.render(), self.manifest])
