"""Initialize a new project for a software application."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import DisplayName


class InitApplicationCommand(Command):
    command_name = 'init'
    args = [
        Argument('name',
            help="the symbolic name of the software application "
                "project. Must be a valid Python identifier."),
        DisplayName('--display-name'),
        Argument('--version',
            help="version of the programming language. If not specified, "
                "most recent is assumed.")
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        spec = {
            'project': {
                'name': args.name,
                'type': 'app'
            }
        }
        params = {
            'project.display_name': Argument.parsestring(args.display_name)
        }
        with self.codebase.commit(f"Initialize software application '{args.name}'", noprefix=True):
            quantum.init('app', args.name, codebase=self.codebase,
                params=params)
            quantum.persist()
