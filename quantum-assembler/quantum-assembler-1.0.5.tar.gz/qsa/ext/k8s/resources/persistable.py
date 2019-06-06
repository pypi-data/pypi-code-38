import os
import io

import yaml


class Persistable:
    """Represents a top-level datastructure that is persistable
    as a Kubernetes resource manifest.
    """
    prefix = "{{ K8S_NAMESPACE_PREFIX }}"
    serializer_args = {'indent': 2, 'default_flow_style': False}

    @property
    def filename(self):
        return f'{self.kind.lower()}.{self.base_qualname}.yml'

    @classmethod
    def getfilename(cls, name, namespace=None):
        if not cls.cluster_wide:
            if not namespace:
                raise TypeError("The `namespace` argument is required.")
            name = f'{namespace}.{name}'
        return f'{cls.kind.lower()}.{name}.yml'

    def render(self, fn, stage=None):
        """Encodes the :class:`Persistable` to a string."""
        dto = self.getmanifest()
        stage = stage or self.stage
        meta = dto.pop('__ansible__')

        header = {
            'vars': meta.vars,
            'when': "target_environment in environments"
        }
        if meta.name:
            header['name'] = meta.name
        header['k8s'] = {
            'state': meta.state,
            'kind': dto.kind,
            'definition': f'k8s/{stage}/{fn}'
        }
        if not self.cluster_wide:
            header['k8s']['namespace'] = self.namespace

        tags = meta.get('tags')
        if tags:
            header['tags'] = tags


        sep = '# ansible:'
        buf = io.StringIO(yaml.safe_dump(header, **self.serializer_args))
        header = '---\n'
        for line in buf.readlines():
            header += f'{sep} {line}'
        return header + yaml.safe_dump(dto, **self.serializer_args)

    def _on_persist(self, repo, dst, fn, new):
        if self.labels:
            self._manifest.metadata.labels = dict(sorted([
                x for x in self.labels.items()], key=lambda x: x[0]))
        self.tags = list(sorted(self.tags))
        return self.on_persist(repo)

    def on_persist(self, repo):
        """Hook that is invoked prior to persisting the object."""
        pass
