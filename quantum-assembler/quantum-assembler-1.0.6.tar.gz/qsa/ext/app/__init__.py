from qsa.ext.base import BaseExtension
from .cli import InitApplicationCommand


class Extension(BaseExtension):
  name = command_name = 'app'
  subcommands = [
    InitApplicationCommand
  ]
