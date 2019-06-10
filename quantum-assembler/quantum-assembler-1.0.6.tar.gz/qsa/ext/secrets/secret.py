import copy
import logging

from qsa.lib.serializers import Base64DER
from .vault import Vault


class SecretMetaclass(type):

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        # A quick and ugly hack.
        if new_class.typename is not None:
            Vault.adapters[new_class.typename] = new_class
        return new_class


class BaseSecret(metaclass=SecretMetaclass):
    typename = None

    def __init__(self, namespaces, name, *args, **kwargs):
        self.name = name
        self.namespaces = namespaces or []

    def addtovault(self, vault):
        """Adds the secret to the vault. Does not persist the vault
        to disk.
        """
        vault.setsecret(self.name, self.dump())


class GenericSecret(BaseSecret):
    """This is a generic secret implementation with no special
    behavior.
    """
    typename = 'generic'

    def __init__(self, namespaces, name, data):
        super().__init__(namespaces, name)
        self.data = data

    def dump(self):
        """Dumps the secret to the local vault storage format."""
        data = {}
        for key in self.data:
            value = self.data[key]
            if not isinstance(value, str):
                # No special stuff for non-strings
                data[key] = value
                continue

            # Do some check if we need block chomping operators
            # etc.
            must_chomp = False

            # If the string starts with five dashes we assume
            # its a certificate (PEM-encoding and similar).
            if str.startswith(value, '-----')\
            or len(value) > 256:
                must_chomp = True

            if must_chomp:
                value = Base64DER(value)

            data[key] = value

        return data


class TLS(BaseSecret):
    typename = "kubernetes.io/tls"

    @classmethod
    def fromfiles(cls, namespaces, name, key, crt):
        """Instantiate a new :class:`TLS` instance from
        filepaths on the local filesystem.
        """
        return cls(namespaces, name,
            open(key).read(), open(crt).read())

    def __init__(self, namespaces, name, key, crt):
        super().__init__(namespaces, name)
        self.key = key
        self.crt = crt

    @classmethod
    def load(cls, dto):
        return cls(dto['metadata']['namespaces'],
            dto['metadata']['name'], dto['data']['tls.key'],
            dto['data']['tls.crt'])

    def dump(self):
        """Dumps the secret to the local vault storage format."""
        return {
            'kind': 'Secret',
            'type': self.typename,
            'metadata': {
                'namespaces': self.namespaces,
                'name': self.name
            },
            'data': {
                'tls.key': Base64DER(self.key),
                'tls.crt': Base64DER(self.crt)
            }
        }


class SecretAdapter:
    """Mocks a secret of a known type for use in the local development
    environment.
    """
    secret_type = None
    logger = logging.getLogger('qsa')

    def __init__(self):
        pass

    def clone(self, secret):
        """Clones the secret into a new datastructure."""
        return copy.deepcopy(secret)

    def is_valid(self, source):
        pass

    def create(self, source):
        raise NotImplementedError

    def update(self, source, target):
        """Updates `target` with the metadata of `source`."""
        if not source.metadata:
            del target.metadata
            return target
        if not target.get('metadata'):
            target.metadata = {}
        target.metadata.update(source.metadata)
        return target


class SecretAdapterManager:
    """Collects :class:`SecretAdapter` instances and provides an interface
    to adapt secrets.
    """

    def __init__(self):
        self._registry = {}
        self._adapters = []

    def register(self, adapter):
        """Registers a :class:`SecretAdapter` implementation."""
        if adapter.secret_type:
            assert adapter.secret_type not in self._registry
            self._registry[adapter.secret_type] = adapter
        else:
            adapters.append(adapter)

    def adapt(self, source, target):
        """Adapts secrets from the source using the appropriate adapter,
        and updates target. Note that target may be ``None``.
        """
        adapter = self._registry.get(source.kind)
        if adapter is not None:
            adapter.is_valid(source)
            target = adapter.create(source) if target is None\
                else adapter.update(source, target)
        else:
            # Loop over all untyped adapters and find the first match.
            pass
        return target
