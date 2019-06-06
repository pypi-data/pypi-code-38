from qsa.lib.datastructures import DTO


class VaultSecret:
    """Represents a secret stored in one of the project
    vaults.
    """

    @property
    def qualname(self):
        return f'{self.namespace}:{self.name}'

    @property
    def name(self):
        return self.metadata.name

    @property
    def namespace(self):
        return self.metadata.namespace

    def __init__(self, repository, namespace, name, data=None, metadata=None, _created=False):
        self.repository = repository
        self.data = data or DTO()
        self.metadata = metadata or DTO()
        self.metadata.update({
            'name': name,
            'namespace': namespace
        })
        self._created = _created
        self.type = None
        assert self.data is not None
        assert self.metadata is not None

    def dump(self):
        """Return a Python dictionary containing a representation
        of the secret in its storage format.
        """
        dto = DTO(data=self.data, metadata=self.metadata,
            kind='Secret', apiVersion="v1")
        if self.type:
            dto.type = self.type
        return dto

    def update(self, **kwargs):
        """Updates the secret with the given arguments."""
        self.data.update(dict(kwargs.get('data', DTO())))
        self.metadata.update(kwargs.get('metadata', DTO()))
        self.type = kwargs.get('type') or None
        assert self.data is not None, kwargs
        assert self.metadata is not None, kwargs

    def isnew(self):
        """Return a boolean if the secret is newly created."""
        return self._created

    def delete(self):
        """Delete the secret from its repository."""
        if self.isnew():
            return
        self.repository.remove(self)

    def persist(self):
        """Persists the secret to the repository."""
        self.repository.add(self)

    def setnamespace(self, namespace):
        """Sets the namespace of the secret to the given value."""
        self.metadata.namespace = namespace
