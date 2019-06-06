import os
import warnings

import ioc

from qsa.ext.base import BaseExtension
from .adapters import ApplicationSecretKeyAdapter
from .adapters import OAuthKeypairAdapter
from .adapters import PublicFacingServerCertificateAdapter
from .cli import AllowKeyCommand
from .cli import CreateVaultCommand
from .cli import CreateCommand
from .cli import ListSecretsCommand
from .cli import InitVaultsCommand
from .cli import ShowSecretCommand
from .secret import SecretAdapterManager
from .secret import TLS
from .schema import ConfigSchema
from .schema import VaultConfigSchema
from .services import VaultSecretImportService
from .vault import Vault
from .vault import VaultManager


class Extension(BaseExtension):
    name = 'secrets'
    command_name = 'secret'
    schema_class = ConfigSchema
    subcommands = [
        {
            'name': 'updatevaults',
            'args': []
        },
        {
            'name': 'update',
            'args': [{'dest': 'vault'}]
        },
        {
            'name': 'edit-vault',
            'args': [
                {'dest': 'vault'}
            ]
        },
        {
            'name': 'synclocal',
            'args': [{'dest': 'vault'}]
        },
        {
            'name': 'checksync',
            'args': [{'dest': 'vault'}]
        },
        AllowKeyCommand,
        CreateCommand,
        ShowSecretCommand,
        ListSecretsCommand,
        InitVaultsCommand,
        CreateVaultCommand
    ]

    supported_projects = ['application', 'k8s']
    codebase = ioc.class_property('core:CodeRepository')

    def allowkey(self, keyid):
        if keyid not in self.spec.secrets.allowed_keys:
            self.spec.secrets.allowed_keys.append(keyid)

    def getallowedkeys(self):
        return self.spec.secrets.allowed_keys

    def setup_injector(self, injector):
        injector.provide('vaults', VaultManager(self.config))
        self.provide_class(VaultSecretImportService())
        self.provide_class(VaultManager(self.config))
        self.provide_class(self)

    def on_project_init(self, quantum, typname, name, *args, **kwargs):
        self.spec = self.schema_class.getfordump().dump({})

    def on_setup_secret_adapters(self, adapters):
        adapters.register(
            PublicFacingServerCertificateAdapter())
        adapters.register(
            ApplicationSecretKeyAdapter())
        adapters.register(
            OAuthKeypairAdapter())

    def handle_create(self, codebase, args, vaults):
        """Handles the creation of a secret."""
        if args.kind != 'tls':
            raise NotImplementedError
        vault = vaults.get('.cluster')
        secret = TLS.fromfiles(args.namespaces, args.name,
            args.key, args.cert)
        secret.addtovault(vault)
        with codebase.commit("Update secrets"):
            vault.persist(codebase)

    def handle_update(self, codebase, args):
        """Updates a specific vault with secrets."""
        vault = Vault.open(codebase.abspath('vault'), args.vault)
        self.assembler.notify('secrets_update', args.vault, vault)

    def initcodebase(self, codebase, deployment, vaults):
        if vaults.isconfigured():
            return
        if not self.getallowedkeys():
            self.fail("Set a GPG key for the initial encryption.")
        dirname = codebase.mkdir('vault')
        codebase.write('vault/open-vault',
            self.render('vault/open-vault.j2'))
        codebase.make_executable('vault/open-vault')
        vaults.setup(codebase)
        vaults.allow(self.getallowedkeys())
        self.assembler.notify('vault_configured', codebase, vaults)

    def handle_updatevaults(self, codebase, vaults, deployment):
        """Ensure that all vaults are created."""
        keys = self.quantum.get('secrets.allowed_keys', [])
        if not keys:
            return
        with self.codebase.commit("Initialized vaults"):
            vaults.initialize(keys)

        for env in deployment.getall():
            if codebase.exists(f'vault/{env.name}.aes'):
                continue
            with self.codebase.commit(f"Initialize vault {env.name}"):
                vaults.create(self.codebase, env.name, keys)


    def handle_allow(self, codebase, quantum, args):
        os.environ['QUANTUM_DEPLOYMENT_ENV'] = args.vault
        if args.vault not in quantum.get('secrets.vaults'):
            self.spec['secrets']['keys'][args.vault] = VaultConfigSchema.defaults()
        if args.keyid not in self.spec['secrets']['vaults'][args.vault]['allowed_keys']:
            self.spec['secrets']['vaults'][args.vault]['allowed_keys'].append(args.keyid)
        with codebase.commit(f"Allowed {args.keyid} to open vault {args.vault}"):
            quantum.update(self.spec)
            quantum.persist(codebase)
        #    vault = Vault.open(codebase.abspath('vault'), args.vault)
        #    vault.setkeys(codebase,
        #        quantum.get(f'secrets.vaults.{args.vault}.keys'))

    def handle_edit_vault(self, codebase, args, vaults):
        """Edit a vault using vim."""
        os.environ['QUANTUM_DEPLOYMENT_ENV'] = args.vault
        dst = codebase.abspath(f'vault/{args.vault}.aes')
        if not os.path.exists(dst):
            self.fail(f"No such vault: {args.vault}")
        vault = vaults.get(args.vault)
        with codebase.commit(f"Edit secrets for {args.vault} environment"):
            vault.editor(codebase)

    def handle_synclocal(self, assembler, codebase, args):
        """Synchronizes the local development environment vault with
        the specified environment for all known secret types.
        """
        adapters = SecretAdapterManager()
        sources = Vault.open(codebase.abspath('vault'), args.vault)
        targets = Vault.open(codebase.abspath('vault'), 'local')
        assembler.notify('setup_secret_adapters', adapters)
        for name, source in sources:
            target = adapters.adapt(source,
                targets.getsecret(name))
            if target is not None:
                targets.setsecret(name, target)
                continue
            self.logger.warning("Unable to adapt secret %s (kind: %s)",
                name, source.kind)

        with codebase.commit(f"Synchronize local vault with {args.vault}"):
            targets.persist(codebase)

    def handle_checksync(self, codebase, args):
        """Checks if all secrets from the source vault are present in the
        local vault.
        """
        sources = Vault.open(codebase.abspath('vault'), args.vault)
        targets = Vault.open(codebase.abspath('vault'), 'local')
        for name, spec in sources:
            present = name in targets
            print(f"checking if {name} (kind: {spec.kind}) is present in local vault....."
                + ('ok' if present else 'MISSING'))

    def handle(self, vaults, deployment):
        """Ensure that vaults for all specified environments exist."""
        if not vaults.isconfigured():
            return

        with self.codebase.commit("Create vaults for specified environments"):
            #vaults.allow(self.getallowedkeys())
            self.assembler.notify('vaults_init', self.codebase, self, vaults)
            self.assembler.notify('vaults_init_complete', vaults)

    def on_vault_required(self, *args, **kwargs):
        self.injector.call(self.initcodebase)
        self.injector.call(self.handle)
