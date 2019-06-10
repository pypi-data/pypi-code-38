import copy
import functools
import io
import os
import paramiko

import ioc
from ansible.plugins.filter.core import b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from qsa.lib import transaction
from qsa.lib.serializers import Base64DER


class SecretMap(dict):

    def add(self, key, value, on_failure=None):
        """Adds a new key to the secret mapping."""
        if key in self:
            if callable(on_failure):
                on_failure(key, value)
            raise ValueError(f"Key {key} exist in mapping.")
        self[key] = value

    def dump(self):
        """Dump the :class:`SecretMap` to it's storage format."""
        return {x: b64encode(y) for x, y in dict.items(self)}


class VaultSecretImportService:
    default_ssh_algorithm = 'rsa'
    manager = ioc.class_property('secrets:VaultManager')
    codebase = ioc.class_property('core:CodeRepository')
    deployments = ioc.class_property('deployment:Extension')

    def import_ssh(self, environment, namespaces, name, username, **kwargs):
        """Import an SSH key. Generate by providing ``generate=True`` or with the
        `src` argument.

        Args:
            environment (string): specifies the environment. Use 'global'
                if the secret is not bound to a specific environment.
            namespaces (list): the namespaces to publish the secret in. At
                least one namespace must be given.
            generate (bool): generate the key.

        Returns:
            None
        """
        data = SecretMap()
        data.add('username', username)
        algo = kwargs.get('algorithm', self.default_ssh_algorithm)
        if algo != 'rsa':
            raise NotImplementedError
        if len(namespaces) > 1 and not generate:
            raise ValueError("Can only import key into one namespace at a time.")
        vault = self.manager.get(environment, create=True)

        # Generate the SSH key.
        buf = io.StringIO()
        key = paramiko.RSAKey.generate(4096)
        key.write_private_key(buf)
        buf.seek(0)

        data.add('id_rsa', buf.read())
        data.add('id_rsa.pub', f'ssh-rsa {key.get_base64()}')

        params = self.skel(name, data=data.dump(), labels=kwargs.get('labels'),
            annotations=kwargs.get('annotations'))
        with transaction.atomic() as tx:
            self._persist(tx, vault, environment, namespaces, name, params)

    def _persist(self, tx, vault, env, namespaces, name, base):
        """Persist a secret in the vault."""
        alias = self.deployments.getalias(env)\
            if env != 'global' else None
        for ns in namespaces:
            params = copy.deepcopy(base)
            if env != 'global':
                ns = f'ns{alias}{ns}'
            secret = vault.decrypt(ns, name)
            if not secret.isnew():
                raise ValueError(f"Secret {name} already exists in {ns}")
            secret.update(**params)
            secret.setnamespace(ns)
            tx.add(secret.persist, secret.delete)
        tx.add(functools.partial(vault.persist, self.codebase))

    def import_generic(self, environment, namespace, name, generate=None, files=None, literals=None,
        annotations=None, labels=None):
        """Import a generic secret into the vault for the
        specified environment. Make the secret available in the
        given `namespaces`.

        Args:
            environment (string): specifies the environment. Use 'global'
                if the secret is not bound to a specific environment.
            namespaces (string): the namespace to publish the secret in.
            name (string): the name of the secret.
            generate (dict): generate random characters for keys.
            files (dict): mapping of keys to files containing secrets.
            literals (mapping): a mapping of keys to literal values.
            labels (dict): labels for the secret.
            annotations (dict): annotations for the secret.

        Returns:
            None
        """
        assert not isinstance(namespace, list)
        data = SecretMap(literals or {})
        for key in (generate or {}):
            data.add(key, bytes.hex(os.urandom(int(generate[key] / 2))))
        for key in (files or {}):
            data.add(key, open(files[key]).read())

        base_params = self.skel(name, data=data.dump(),
            annotations=annotations, labels=labels)
        vault = self.manager.get(environment, create=True)
        alias = self.deployments.getalias(environment)\
            if environment != 'global' else None
        with transaction.atomic() as tx:
            params = copy.deepcopy(base_params)
            if environment != 'global':
                namespace = f'ns{alias}{namespace}'
            secret = vault.decrypt(namespace, name)
            if not secret.isnew():
                raise ValueError(f"Secret {name} already exists in {namespace}")
            secret.update(**params)
            secret.setnamespace(namespace)
            tx.add(secret.persist, secret.delete)
            tx.add(functools.partial(vault.persist, self.codebase))

    def import_tls(self, environment, namespaces, name, key, crt, annotations=None, labels=None, noprefix=False):
        """Import a TLS certificate and key into the vault for the
        specified environment. Make the secret available in the
        given `namespaces`.

        Args:
            environment (string): specifies the environment. Use 'global'
                if the certificate/key are not bound to a specific
                environment.
            namespaces (list): the namespaces to publish the secret in. At
                least one namespace must be given.
            name (string): the name of the secret.
            key (string): points to the location of the private key.
            crt (string): points to the location of the public key.
            labels (dict): labels for the secret.
            annotations (dict): annotations for the secret.

        Returns:
            None
        """
        vault = self.manager.get(environment, create=True)
        secrets = []
        base_params = {
            'type': "kubernetes.io/tls",
            'data': SecretMap({
                'tls.key': b64encode(open(key).read()),
                'tls.crt': b64encode(open(crt).read())
            }),
            'metadata': {
                'name': name,
                'annotations': annotations or {},
                'labels': labels or {}
            }
        }
        base_params['metadata']['annotations'].update({
            'meta.quantumframework.org/encoding': "base64"
        })
        alias = self.deployments.getalias(environment)\
            if environment != 'global' else None
        with transaction.atomic() as tx:
            for ns in namespaces:
                params = copy.deepcopy(base_params)
                if environment != 'global' and not noprefix:
                    ns = f'ns{alias}{ns}'
                secret = vault.decrypt(ns, name)
                if not secret.isnew():
                    raise ValueError(f"Secret {name} already exists in {ns}")
                secret.update(**params)
                secret.setnamespace(ns)
                tx.add(secret.persist, secret.delete)
            tx.add(functools.partial(vault.persist, self.codebase))

    def skel(self, name, labels=None, annotations=None, data=None, string_data=None):
        """Return a dictionary that is a skeleton to instantiate
        a secret.
        """
        skel = {
            'data': data or {},
            'metadata': {
                'name': name,
                'annotations': annotations or {},
                'labels': labels or {}
            }
        }
        skel['metadata']['labels'].update({
            'app.kubernetes.io/managed-by': 'qsa-cli',
            'app.kubernetes.io/name': name
        })
        skel['metadata']['annotations'].update({
            'meta.quantumframework.org/encoding': "base64"
        })
        return skel

    def _dump(self, data):
        return SecretMap.dump(data)\
            if isinstance(data, SecretMap)\
            else {x: b64encode(y) for x,y in dict.items(data)}
