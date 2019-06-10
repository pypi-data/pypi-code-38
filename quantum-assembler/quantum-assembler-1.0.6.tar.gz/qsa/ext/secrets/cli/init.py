"""Initialize all vaults for the current project."""
import os

import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.ext.secrets import const


class InitVaultsCommand(Command):
    command_name = 'init'
    help_text   = __doc__
    codebase = ioc.class_property('core:CodeRepository')
    vaults = ioc.class_property('secrets:VaultManager')
    deployment = ioc.class_property('deployment:Extension')
    args = [
        Argument('--keyid', default=os.getenv('QSA_PGP_KEY'),
            help="specifies the initial PGP key to encrypt the vaults with.")
    ]

    def handle(self, quantum, args):
        if not args.keyid:
            self.fail(
                "Provide a PGP key id using the --keyid parameter or "
                "set the QSA_PGP_KEY environment variable."
            )
        self.message(f"Encrypting the vault AES-256 secret with PGP key {args.keyid}")
        with self.codebase.commit("Initialize project vaults", noprefix=True):
            self.vaults.initialize([args.keyid])
            if not quantum.get('secrets.allowed_keys', None):
                quantum.update({
                    'secrets': {
                        'allowed_keys': [args.keyid]
                    }
                })
            quantum.persist(self.codebase)
            for env in self.deployment.getall():
                if self.vaults.exists(env.name):
                    continue
                self.vaults.create(self.codebase, env.name, [args.keyid])
