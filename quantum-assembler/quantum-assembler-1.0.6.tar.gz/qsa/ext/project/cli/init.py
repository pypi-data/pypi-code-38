"""Initialize a new Quantum project."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList
from qsa.lib.cli import Selectors


class InitProjectCommand(Command):
    command_name = 'init'
    help_text = __doc__
    args = [
        Argument('project_type',
            help="specifies the project type."),
        Argument('name', help="specifies the symbolic name of the project."),
        Argument('--display-name', nargs='+', required=True,
            help="a display name for this project.")
    ]
    codebase = ioc.class_property('core:CodeRepository')
    project = ioc.class_property('project:Extension')

    def handle(self, args, quantum):
        args.display_name = str.join(' ', args.display_name)
        with self.codebase.commit(f"Initialize project {args.display_name}", noprefix=True):
            quantum.init(args.project_type, args.name,
                params={'display_name': args.display_name})
            quantum.persist()
