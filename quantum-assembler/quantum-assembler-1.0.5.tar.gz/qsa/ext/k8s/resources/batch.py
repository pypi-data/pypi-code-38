import collections


class ResourceBatch:
    """Provides an API for batch operations on resources."""

    def __init__(self, resources):
        self.resources = collections.OrderedDict()
        for t in resources:
            if not t.cluster_wide:
                self.resources[f'{t.metadata.namespace}-{t.metadata.name}'] = t
            else:
                self.resources[f'cluster:{t.name}'] = t

    def all(self, func):
        return all([func(x) for x in self.resources.values()])

    def setunbound(self, *args, **kwargs):
        """Sets the containers as not bound to an environment."""
        [x.setunbound(*args, **kwargs) for x in self.resources.values()]
        return self

    def setenvironments(self, *args, **kwargs):
        """Sets the environments all :class:`Resource` objects."""
        [x.setenvironments(*args, **kwargs) for x in self.resources.values()]
        return self

    def get(self, qualname):
        """Return a resource by it's qualified name."""
        return self.resources[qualname]

    def label(self, *args, **kwargs):
        [x.label(*args, **kwargs) for x in self.resources.values()]
        return self

    def persist(self, repo, *args, **kwargs):
        for resource in self.resources.values():
            repo.add(resource)

    def dump(self):
        return [x.dump() for x in self.resources.values()]
