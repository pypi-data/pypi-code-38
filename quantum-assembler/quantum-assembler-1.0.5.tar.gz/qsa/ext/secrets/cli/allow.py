"""Allow a PGP key to open the vault. The public key must be
present on the local machines' keyring (keys are not fetched
from PGP keyservers)."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument



class AllowKeyCommand(Command):
    command_name = 'allow'
    help_text = __doc__
    codebase = ioc.class_property('core:CodeRepository')
    secrets = ioc.class_property('secrets:Extension')
    args = [
        Argument('keyid', help="the PGP key to allow open the vault."),
    ]

    def handle(self, quantum, args):
        self.secrets.allowkey(args.keyid)
        with self.codebase.commit(f"Allowed {args.keyid} to open the vault.", noprefix=True):
            quantum.persist(self.codebase)
