"""Create a new vault with the specified name and key."""
import os

import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument



class CreateVaultCommand(Command):
    command_name = 'createvault'
    help_text = __doc__
    codebase = ioc.class_property('core:CodeRepository')
    vaults = ioc.class_property('secrets:VaultManager')
    args = [
        Argument('name',
            help="specifies the name of the vault."),
        Argument('--keyid', default=os.getenv('QSA_PGP_KEY'),
            help="the PGP key to allow open the vault."),
    ]

    def handle(self, quantum, args):
        if self.vaults.exists(args.name):
            self.fail(f"Vault exists: {args.name}")
        if not args.keyid:
            self.fail(
                "Provide a PGP key id using the --keyid parameter or "
                "set the QSA_PGP_KEY environment variable."
            )
        with self.codebase.commit(f"Create vault {args.name}", noprefix=True):
            if not self.vaults.isconfigured():
                self.vaults.initialize([args.keyid])
            vault = self.vaults.create(self.codebase, args.name, [args.keyid])
            if quantum.exists():
                quantum.persist(self.codebase)
