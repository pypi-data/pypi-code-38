"""Output a secret to the command line."""
import ioc
from ansible.plugins.filter.core import b64decode

from qsa.lib.cli import Command
from qsa.lib.cli import Argument


class ShowSecretCommand(Command):
    vaults = ioc.class_property('secrets:VaultManager')
    command_name = 'show'
    args = [
        Argument('env', help="environment to create the secret in."),
        Argument('namespace',
            help="the namespace."),
        Argument('name',
            help="the name of the secret within its namespace."),
        Argument('key',
            help="the key to show"),
    ]

    def handle(self, args):
        secret = self.vaults.decrypt(args.env, args.namespace, args.name)
        try:
            value = secret.data[args.key]
            if secret.metadata.annotations.get('meta.quantumframework.org/encoding') == 'base64':
                value = b64decode(value)
            print(value)
        except LookupError:
            self.fail(f"No such key in {args.env}/{args.namespace}.{args.name}: {args.key}")
