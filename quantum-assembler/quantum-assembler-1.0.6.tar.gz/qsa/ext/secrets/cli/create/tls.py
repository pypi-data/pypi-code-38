"""Import a keypair for TLS encryption."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Enable


class TLSCommand(Command):
    codebase = ioc.class_property('core:CodeRepository')
    vaults = ioc.class_property('secrets:VaultSecretImportService')
    command_name = 'tls'
    args = [
        Argument('name',
            help="the name of the secret within its namespace."),
        Argument('--key', required=True,
            help="the filepath to a private key."),
        Argument('--cert', required=True,
            help="the filepath to a certificate"),
        ArgumentList('-n', required=True, dest='namespaces',
            help="namespace(s) to create the secret in."),
        Argument('-e', required=True, dest='environment',
            help="environment to create the secret in."),
        Enable('--noprefix',
            help="do not prefix the namespace.")
    ]

    def handle(self, assembler, args):
        with self.codebase.commit("Update secrets", noprefix=True):
            assembler.notify('vault_required')
            self.vaults.import_tls(args.environment, args.namespaces,
                args.name, args.key, args.cert, noprefix=args.noprefix)
