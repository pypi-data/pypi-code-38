"""Updates the specified key in the secret."""
import itertools

import ioc
from ansible.plugins.filter.core import b64encode

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from .commandlineinputmixin import CommandLineInputMixin


class SetKeyCommand(Command, CommandLineInputMixin):
    vaults = ioc.class_property('secrets:VaultManager')
    codebase = ioc.class_property('core:CodeRepository')
    command_name = 'set'
    args = [
        Argument('env', help="environment holding the secret."),
        Argument('namespace',
            help="the namespace."),
        Argument('name',
            help="the name of the secret within its namespace."),
        ArgumentList('--from-file',
            help="create a secret from a file."),
        ArgumentList('--from-literal', dest='literals', type=Command.parseopt,
            help="create a secret from a literal command-line argument."),
    ]

    def handle(self, args):
        if not self.vaults.exists(args.env):
            self.fail(f"No such environment: {args.env}")
        secret = self.vaults.decrypt(args.env, args.namespace, args.name)
        if secret.isnew():
            self.fail(f"No such secret in environment "
                       "{args.env}: {args.namespace}/{args.name}")

        values = self._parse_from_generated(args.from_file)
        for key in list(values.keys()):
            values[key] = open(values[key]).read()
        values.update(dict(args.literals))

        for key, value in dict.items(values):
            secret.setkeyfromstring(key, value)

        with self.codebase.commit("Modified vaults", noprefix=True):
            secret.persist()
            secret.flush(self.codebase)
