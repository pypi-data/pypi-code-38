from qsa.ext.base import BaseExtension

from .model import Makefile


class Extension(BaseExtension):
    name = command_name = 'make'

    def handle(self, codebase):
        mk = Makefile(self.assembler, self.spec)
        with codebase.commit("Compile Makefile"):
            self.render_to_file(codebase, 'Makefile.j2',
                'Makefile', ctx={'make': mk})

    def on_setup_makefile(self, mk):
        """Adds the common QSA Makefile targets."""
        mk.target('clean')
        mk.target('env')
        mk.setvariable('QSA', 'qsa')
        build = mk.target('build')

    def on_setup_makefile_target_clean(self, mk, target):
        target.execute('rm -rf ./var')
        target.execute('rm -rf ./env')
        target.execute('rm -rf ./build')
        target.execute('rm -rf ./dist')
        target.execute('find . -type d -name __pycache__ -exec rm -r {} \+')

    def on_setup_makefile_target_env(self, mk, target):
        target.execute('pip3 install quantum-assembler --upgrade')
