"""Initialize a new project for a software application."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument


class InitApplicationCommand(Command):
    command_name = 'init'
    args = [
        Argument('language',
            help="specifies the main language of the software "
                "application."),
        Argument('name',
            help="the symbolic name of the software application "
                "project. Must be a valid Python identifier."),
        Argument('--version',
            help="version of the programming language. If not specified, "
                "most recent is assumed.")
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, args):
        spec = {
            'project': {
                'name': args.name,
                'type': 'app',
                'language': args.language
            }
        }
        if args.version:
            spec['project']['language'] += f':{args.version}'
        with self.codebase.commit(f"Initialize software application '{args.name}'", noprefix=True):
            quantum.init('app', args.name, codebase=self.codebase)
            quantum.spec['project']['language'] = args.language
            quantum.persist()
