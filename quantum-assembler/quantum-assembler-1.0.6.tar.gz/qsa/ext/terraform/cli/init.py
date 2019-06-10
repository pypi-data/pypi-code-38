"""Initialize a Terraform project."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Argument
from qsa.lib.cli import ArgumentList


class InitCommand(Command):
    command_name = 'init'
    help_text = __doc__
    args = [
        Argument('name',
            help="a symbolic name describing the project."),
        Argument('--display-name', nargs='+',
            help="an optional display name describing the project."),
        Argument('--ci',
            help="specifies the CI server implementation.")
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, quantum, project, template, args):
        with self.codebase.commit("Initialized Terraform project", noprefix=True):
            params = {
                'ci.using': args.ci,
                'project.display_name': Argument.parsestring(args.display_name)
            }
            quantum.init('terraform', args.name, params=params)
            quantum.persist()
            if not self.codebase.exists('variables.tf'):
                self.codebase.write('variables.tf', '')
            if not self.codebase.exists('main.tf'):
                self.codebase.write('main.tf', '')
            if not self.codebase.exists('modules'):
                self.codebase.mkdir('modules')
            template.render_to_file('Jenkinsfile.terraform', 'Jenkinsfile')

