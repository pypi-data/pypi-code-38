"""Create secrets of various kinds."""
from qsa.lib.cli import Command
from .generic import CreateGenericSecret
from .ssh import GenerateRSACommand
from .tls import TLSCommand


class CreateCommand(Command):
    command_name = 'create'
    subcommands = [
        TLSCommand,
        CreateGenericSecret,
        GenerateRSACommand
    ]
    help_text = (
        "Specify the secret to create. For a list of valid secret names, "
        "run qsa secret create --help"
    )

