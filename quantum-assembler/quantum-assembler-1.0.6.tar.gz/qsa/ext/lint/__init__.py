import functools

from qsa.lib.datastructures import ImmutableDTO
from qsa.ext.base import BaseExtension
from .languages import YAMLDetector


class Extension(BaseExtension):
    name = inject  = 'lint'

    @property
    def opts(self):
        return self.getlanguages()

    @functools.lru_cache(maxsize=128)
    def getlanguages(self):
        return ImmutableDTO.fromdict({
            'LINT_YAML': YAMLDetector().detect()
        })

    def handle(self, codebase):
        """Creates configuration files for the detected languages,
        if they do not exist.
        """
        if self.opts.LINT_YAML and not codebase.exists('.yamllint'):
            with codebase.commit("Add YAML linting configuration"):
                self.render_to_file(codebase, 'yaml.conf.j2', '.yamllint')

    def on_setup_makefile(self, make):
        """Adds targets for each detected linting language."""
        if not any([bool(x) for x in self.opts.values()]):
            return
        c = (
            "docker run --rm -it -v $(CURDIR):/app -w /app\\\n\t\t"
            "quantumframework/{image}\\\n\t\t"
            "/usr/local/bin/run-lint"
        )

        # Add a global target that runs all linting.
        lint = make.target('lint')

        if self.opts.LINT_YAML:
            t = make.target('lint-yaml')
            t.execute(c.format(image='agent-lint-yaml:latest'))
            lint.execute('make lint-yaml')

    def on_pipeline_render(self, ctx):
        ctx.update({
            'MUST_LINT': any(self.opts.values())
        })
        ctx.update(self.opts)
