"""Lists all secrets in the vault."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import ArgumentList



class ListSecretsCommand(Command):
    command_name = 'ls'
    help_text = __doc__
    vaults = ioc.class_property('secrets:VaultManager')
    args = [
        ArgumentList('-v', dest='vaults',
            help="specify the vault(s) to list secrets for."),
    ]

    def handle(self, args):
        for vault_name in args.vaults:
            vault = self.vaults.get(vault_name)
            for secret in vault.itersecrets():
                print(f'{vault_name}\t{secret.metadata.namespace}\t{secret.metadata.name}')
