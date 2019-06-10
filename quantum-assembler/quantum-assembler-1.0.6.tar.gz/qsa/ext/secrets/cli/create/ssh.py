"""Import or generate a SSH keypair"""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import Enable
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Annotations
from qsa.lib.cli import Labels


class GenerateRSACommand(Command):
    codebase = ioc.class_property('core:CodeRepository')
    vaults = ioc.class_property('secrets:VaultSecretImportService')
    command_name = 'ssh+rsa'
    args = [
        Argument('environment',
            help="environment to create the secret in."),
        Argument('namespace',
            help="the namespace to create the secret in."),
        Argument('name',
            help="the name of the secret within its namespace."),
        Argument('username',
            help="the default username associated to the SSH key."),
        Enable('--generate', action='store_true',
            help="generate a new key."),
        Annotations('-a'),
        Labels('-l')
    ]

    def handle(self, assembler, args):
        with self.codebase.commit("Update secrets", noprefix=True):
            assembler.notify('vault_required')
            self.vaults.import_ssh(args.environment, [args.namespace],
                args.name, args.username, labels=Labels.parse(args.labels),
                annotations=Annotations.parse(args.annotations),
                generate=args.generate)
