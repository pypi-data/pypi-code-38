"""Create a generic secret mapping."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Annotations
from qsa.lib.cli import Labels


class CreateGenericSecret(Command):
    max_password_length = 32
    codebase = ioc.class_property('core:CodeRepository')
    vaults = ioc.class_property('secrets:VaultSecretImportService')
    command_name = 'generic'
    args = [
        Argument('env', help="environment to create the secret in."),
        Argument('namespace',
            help="namespace to create the secret in."),
        Argument('name',
            help="the name of the secret within its namespace."),
        ArgumentList('--from-generated',
            help="generated a random sequence of alphanumeric characters."),
        ArgumentList('--from-file',
            help="create a secret from a file."),
        ArgumentList('--from-literal', dest='literals', type=Command.parseopt,
            help="create a secret from a literal command-line argument."),
        Annotations('-a'),
        Labels('-l')
    ]

    def handle(self, assembler, args):
        assembler.notify('vault_required')
        with self.codebase.commit("Update secrets", noprefix=True):
            self.vaults.import_generic(args.env, args.namespace, args.name,
                generate=self._parse_from_generated(args.from_generated, self._validate_length),
                files=self._parse_from_generated(args.from_file),
                literals=dict(args.literals), annotations=Annotations.parse(args.annotations),
                labels=Labels.parse(args.labels))

    def _parse_from_generated(self, args, f=None):
        params = {}
        f = f or (lambda x: x)
        for arg in args:
            if str.count(arg, '=') != 1:
                self.fail(f"Invalid format : {arg}")
            key, length = str.split(arg, '=')
            params[key] = f(length)

        return params

    def _validate_length(self, length):
        if not length.isdigit():
            self.fail("Argument after = must be numeric.")
        length = int(length)
        if length > self.max_password_length:
            self.fail(f"Maximum length is {self.max_password_length}")
        return length
