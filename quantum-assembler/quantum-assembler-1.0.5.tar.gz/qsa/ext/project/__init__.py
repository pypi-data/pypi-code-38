import ioc

from qsa.ext.base import BaseExtension
from .cli import InitProjectCommand
from .schema import ConfigSchema


class Extension(BaseExtension):
    codebase = ioc.class_property('core:CodeRepository')
    name = command_name = inject = 'project'
    schema_class = ConfigSchema
    subcommands = [
        {
            'name': 'configure',
            'args': [
                ('--display-name', {'nargs': '+'})
            ]
        },
        InitProjectCommand
    ]

    @property
    def display_name(self):
        return self.spec.project.display_name or self.symbolic_name

    @property
    def symbolic_name(self):
        return self.spec.project.name

    @property
    def safe_type(self):
        return str.replace(self.spec.project.type, '+', '-')

    def setdisplayname(self, display_name):
        """Sets the display name for this project."""
        self.spec.display_name = display_name
        quantum.update(self.spec)

    def on_project_init(self, quantum, typname, name, *args, **kwargs):
        params = kwargs.get('params') or {}
        self.spec = {
            'project': {
                'name': name,
                'type': typname,
                'display_name': params.get('display_name')
            }
        }
        if kwargs.get('language'):
            self.spec['project']['language'] = kwargs['language']
        quantum.update(self.spec)

    def handle_configure(self, args, codebase):
        if args.display_name:
            with self.codebase.commit("Configure display name", noprefix=True):
                self.spec.project.display_name = ' '.join(args.display_name)
                self.quantum.update(self.spec)
                self.quantum.persist()

    def on_pipeline_render(self, ctx):
        ctx.update({
            'DISPLAY_NAME': self.display_name
        })
