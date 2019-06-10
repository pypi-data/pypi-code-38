"""Initialize Ansible for the Quantum project."""
import ioc

from qsa.lib.cli import Command
from qsa.lib.cli import Enable


class InitAnsibleCommand(Command):
    command_name = 'init'
    help_text = __doc__
    args = [
        Enable('--with-vaults',
            help="create vaults for all environments.")
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, assembler, args, ops, ansible):
        if self.codebase.exists('ansible.cfg'):
            self.fail("Ansible is already configured for this project.")
        for env in ops.getenvironments():
            ansible.on_environment_created(env)
