import jinja2
import ioc
import yaml

from qsa.lib.datastructures import DTO
from qsa.ext.base import BaseExtension


class Extension(BaseExtension):
    name = inject = 'template'
    codebase = ioc.class_property('core:CodeRepository')

    def on_extensions_loaded(self, extensions):
        """Adds the loaders of all extension to our template
        engine.
        """
        template = jinja2.Environment(
            loader=jinja2.ChoiceLoader(
                [x.loader for x in extensions if (x != self)]
                + [jinja2.PackageLoader('qsa', 'templates')]),
            **self.template_params
        )
        template.globals.update(self.template.globals)
        template.filters.update(self.template.filters)
        self.template = template
        self.provide_class(self)

    def render_to_file(self, template_name, dst, **ctx):
        """Renders the template to a file with the given context."""
        self.codebase.write(dst,
            self.render_to_string(template_name, **ctx))

    def render_to_string(self, template_name, **ctx):
        """Renders a template identified by `template_name`
        to a string using the given context `ctx`.
        """
        t = self.template.get_template(template_name)
        if self.quantum.exists():
            ctx.update({
                'quantum': self.quantum.spec,
                'PROJECT_NAME': self.quantum.get('project.name')
            })
        self.assembler.notify('template_render', ctx)
        return t.render(**ctx)

    def render_to_yaml(self, *args, **kwargs):
        """Renders a template and loads it as YAML."""
        return DTO.fromdict(yaml.safe_load(self.render_to_string(*args, **kwargs)))
