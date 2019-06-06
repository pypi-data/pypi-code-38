import collections

import ioc


class TagList:
    """Parses the tags into a dictionary."""

    @property
    def task_qualname(self):
        return self.get('qualname',
            'ansible.quantumframework.org')

    @classmethod
    def qualnamefromtask(cls, task):
        return cls(task).task_qualname

    def __init__(self, tags, domain=None):
        self.domain = domain
        self.tags = collections.defaultdict(dict)
        for t in tags:
            key, value = str.split(t, ':', 1)
            domain, key = str.split(key, '/', 1)
            if key in self.tags[domain]:
                if isinstance(self.tags[domain][key], str):
                    self.tags[domain][key] = [ self.tags[domain][key] ]
                self.tags[domain][key].append(value)
            else:
                self.tags[domain][key] = value

    def get(self, key, domain=None):
        """Return the given key from the tags."""
        domain = domain or self.domain
        if domain is None:
            raise ValueError("Provide the `domain` parameter or set default.")
        return self.tags.get(domain, {}).get(key)

    def get_task_impl(self):
        """Return the concrete :class:`Task` implementation
        based on the metadata in the tags.
        """
        qualname = self.get('task-impl',
            'ansible.quantumframework.org')
        if not qualname:
            raise LookupError("ansible.quantumframework.org/task-impl not defined in tags.")
        return ioc.loader.import_symbol(qualname)

    def __iter__(self):
        for domain in self.tags:
            for key in self.tags[domain]:
                yield self.tags[domain][key]

