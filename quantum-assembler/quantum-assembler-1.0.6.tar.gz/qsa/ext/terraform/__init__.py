from qsa.ext.base import BaseExtension
from .cli import InitCommand


class Extension(BaseExtension):
    name = 'terraform'
    command_name = 'terraform'
    subcommands = [
        InitCommand
    ]
