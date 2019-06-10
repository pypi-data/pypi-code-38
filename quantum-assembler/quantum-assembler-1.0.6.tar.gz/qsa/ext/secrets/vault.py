import collections
import os
import subprocess
import tempfile

import gnupg
import ioc
from ansible import constants as C
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import AnsibleVaultError
from ansible.parsing.vault import VaultLib
from ansible.parsing.vault import VaultSecret
from ansible.cli import CLI
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from qsa.cli.exc import CommandError
from qsa.lib.datastructures import DTO
from qsa.lib.serializers import yaml
from .model import VaultSecret
from .const import GLOBAL_VAULT_NAME


class Vault:
    """Provides an API to create and edit an encrypted container of
    secrets.
    """
    adapters = {}

    @staticmethod
    def get(key=None):
        """Returns a :class:`ansible.parsing.VaultLib` instance."""
        if key is None:
            loader = DataLoader()
            vault_secret = CLI.setup_vault_secrets(
                loader=loader,
                vault_ids=C.DEFAULT_VAULT_IDENTITY_LIST,
                vault_password_files=['vault/open-vault']
            )
        else:
            vault_secret = [(DEFAULT_VAULT_ID_MATCH, VaultSecret(key))]
        return VaultLib(vault_secret)

    @classmethod
    def create(cls, codebase, vault_dir, name, keys=None):
        """Create a new vault in the specified directory."""
        vault = cls.get()
        buf = vault.encrypt('---\n{}')
        codebase.write(f'{vault_dir}/{name}.aes', buf,
            mode='wb', newline=False)
        return vault

    @classmethod
    def createlocal(cls, codebase, vault_dir, name, *args, **kwargs):
        """Creates the vault that is used in the local development
        environment. This vault is not used to store "real" secrets;
        it exists solely to provide integration with the local
        development tools.
        """
        key = bytes.hex(AESGCM.generate_key(256))
        codebase.write(f'{vault_dir}/{name}.txt', key)
        vault = cls.get(key=str.encode(key))
        buf = vault.encrypt('')
        codebase.write(f'{vault_dir}/{name}.aes', buf,
            mode='wb', newline=False)

    @classmethod
    def open(cls, manager, dirname, name, keys=None):
        fp = os.path.join(dirname, f'{name}.aes')
        assert os.path.exists(fp), fp
        plain = os.path.join(dirname, f'{name}.txt')
        key = None
        if os.path.exists(plain):
            key = open(plain).read()
        try:
            env = os.environ.pop('QUANTUM_DEPLOYMENT_ENV', '')
            os.environ['QUANTUM_DEPLOYMENT_ENV'] = name
            vault = cls.get(key=str.encode(str.strip(key)) if key else None)
            try:
                buf = bytes.decode(vault.decrypt(open(fp).read()))
            except AnsibleVaultError as e:
                raise CommandError(str(e))
            return cls(manager, dirname, name, vault, buf)
        finally:
            if env:
                os.environ['QUANTUM_DEPLOYMENT_ENV'] = env
            else:
                os.environ.pop('QUANTUM_DEPLOYMENT_ENV')

    @property
    def path(self):
        return os.path.join(self.vault_dir, f'{self.name}.aes')

    def __init__(self, manager, vault_dir, name, codec, content):
        self.manager = manager
        self.vault_dir = vault_dir
        self.name = name
        self.content = content
        self.data = None
        self.codec = codec

    def editor(self, codebase):
        """Edit the vault in the system editor."""
        src = tempfile.mktemp()
        with open(src, 'w') as f:
            f.write(self.content)
        args = ['vim', '-c', "'set syntax=yaml ts=2 sw=2 expandtab'", src]
        os.system(' '.join(args))

        # Read the temporary file and write it to the vault
        # destination.
        with open(src) as f:
            content = f.read()
        if content != self.content:
            self.content = content
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
            self.secrets = SecretRepository(self, self.data.get('secrets') or [])
            self.persist(codebase)

    def persist(self, codebase):
        """Persists the contents of the vault."""
        if self.secrets:
            self.data['secrets'] = self.secrets.dump()
        if self.data:
            self.content = '---\n' + yaml.safe_dump(self.data,
                default_flow_style=False, indent=2)
        codebase.write(self.path, self.codec.encrypt(self.content),
            mode='wb', newline=False)

    def setsecret(self, name, spec):
        if self.data is None:
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
            self.secrets = SecretRepository(self, self.data.get('secrets') or [])
        self.data[name] = spec

    def getsecret(self, name):
        """Return the decrypted secret identified by name."""
        if self.data is None:
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
            self.secrets = SecretRepository(self, self.data.get('secrets') or [])
            assert isinstance(self.data, dict)
        value = self.data.get(name)
        return self.adapters[value['type']]\
            .load(value) if value is not None else None

    def decrypt(self, namespace, name, create=True):
        """Decrypts a secret from `namespace` with `name`."""
        if self.data is None:
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
            self.secrets = SecretRepository(self, self.data.get('secrets') or [])
        return self.secrets.get(namespace, name, create=create)

    def itersecrets(self):
        if self.data is None:
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
        return iter(sorted(self.data.get('secrets') or [],
            key=lambda x: (x.metadata.namespace, x.metadata.name)))

    def __iter__(self):
        for name, spec in (yaml.safe_load(self.content) or {}).items():
            yield name, DTO.fromdict(spec)

    def __contains__(self, value):
        if self.data is None:
            self.data = DTO.fromdict(yaml.safe_load(self.content) or {})
            self.secrets = SecretRepository(self, self.data.get('secrets') or [])
        return value in self.data


class SecretRepository:

    def __init__(self, vault, secrets):
        self.vault = vault
        self.secrets = collections.OrderedDict()
        for secret in secrets:
            self.secrets[f'{secret.metadata.namespace}:{secret.metadata.name}'] = secret

    def add(self, secret):
        """Adds a secret to the repository."""
        self.secrets[secret.qualname] = secret.dump()

    def get(self, ns, name, create=False):
        """Get a new secret from the repository. Use the `create`
        parameter to allow creation if it does not exist.
        """
        dto = self.secrets.get(f'{ns}:{name}')
        if dto is None:
            dto = {'namespace': ns, 'name': name, '_created': True}
        else:
            # TODO: Fix API
            dto.update({
                'namespace': dto.metadata.namespace,
                'name': dto.metadata.name
            })
            assert dto.kind == 'Secret'
            dto.pop('kind')
            dto.pop('apiVersion')
            dto.pop('type', None)
        return VaultSecret(self, **dto)

    def remove(self, secret):
        """Removes a secret from the repository."""
        return bool(self.secrets.pop(secret.qualname, None))

    def dump(self):
        """Dump the current state of the repository to a Python
        list.
        """
        return list(self.secrets.values())


class VaultManager:
    """Manages access to the vaults."""
    vault_dir = 'vault'
    codebase = ioc.class_property('core:CodeRepository')
    template = ioc.class_property('template:Extension')

    def __init__(self, config):
        self.config = config

    def isconfigured(self):
        """Return a boolean indicating if the vault secret has been
        set up.
        """
        return self.codebase.exists('vault/vault.pgp')\
            and self.codebase.exists('vault/open-vault')

    def initialize(self, keys):
        """Ensure that the necessary files to open the vault
        exist.
        """
        self.codebase.mkdir('vault')
        if not self.codebase.exists('open-vault'):
            self.template.render_to_file('vault/open-vault.j2',
                'vault/open-vault')
            self.codebase.make_executable('vault/open-vault')
        if not self.codebase.exists('vault/vault.pgp'):
            self.setup(self.codebase, keys)
        if not self.exists(GLOBAL_VAULT_NAME):
            self.create(self.codebase, GLOBAL_VAULT_NAME, keys)

    def decrypt(self, env, namespace, name):
        """Decrypt the secret identified by the given parameters."""
        vault = self.get(env)
        return vault.decrypt(namespace, name, create=False)

    def setup(self, codebase, keys=None):
        """Generate a key and encrypt it with the specified GPG
        key.
        """
        gpg = gnupg.GPG()
        path = codebase.mkdir(self.vault_dir)
        if not keys:
            assert os.getenv('QSA_GPG_KEY'), "Ensure that QSA_GPG_KEY is set."
        assert path
        if os.path.exists('vault/vault.pgp'):
            key = str(gpg.decrypt(open('vault/vault.pgp').read()))
        else:
            key = bytes.hex(AESGCM.generate_key(256))

        # Create the password file and encrypt it using the GPG
        # keys configured for this vault.
        buf = str(gpg.encrypt(key, keys or [os.getenv('QSA_GPG_KEY')],
            always_trust=True))
        assert buf
        codebase.write(f'{self.vault_dir}/vault.pgp', buf)

    def create(self, codebase, name, keys=None):
        """Creates the vault using the given string `name`."""
        keys = keys or []
        assert os.getenv('QSA_GPG_KEY') or keys, "Ensure that QSA_GPG_KEY is set."
        vault_dir = codebase.abspath(self.vault_dir)
        if not codebase.exists(self.vault_dir):
            codebase.mkdir(self.vault_dir)
        if os.getenv('QSA_GPG_KEY'):
            keys.append(os.getenv('QSA_GPG_KEY'))
        return Vault.create(codebase, vault_dir, name, keys=keys)

    def get(self, name, create=False):
        """Return the vault identified by `name`."""
        # TODO: This is a hack. The open-vault script determines the
        # vault to open based on the QUANTUM_DEPLOYMENT_ENV environment
        # variable.
        if create and not self.exists(name):
            self.create(self.codebase, name)
        os.environ['QUANTUM_DEPLOYMENT_ENV'] = name
        return Vault.open(self, 'vault', name)

    def exists(self, name):
        """Return a boolean indicating if a vault with the given
        name exists.
        """
        return os.path.exists(f'vault/{name}.aes')

    def allow(self, keys):
        assert keys
        gpg = gnupg.GPG()
        args = ['vault/open-vault']
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        key, err = p.communicate()
        assert key, key
        if p.returncode != 0:
            raise RuntimeError(key, err)
        buf = gpg.encrypt(key, keys)
        print(keys)
        assert buf.status == 'encryption ok', buf.status
        self.codebase.write(f'{self.vault_dir}/vault.pgp', str(buf))
