import ioc

from qsa.ext.base import BaseExtension
from .schema import ConfigSchema


class Extension(BaseExtension):
    name = command_name = inject = 'jenkins'
    schema_class = ConfigSchema
    weight = 9.1
    subcommands = [
        {
            'name': 'configure',
            'args': [
                ('--folder', {'dest': 'folder'}),
                ('--mounted-secret', {'action': 'append', 'default': [],
                    'dest': 'mounted_secrets'})
            ]
        }
    ]
    codebase = ioc.class_property('core:CodeRepository')

    def handle(self, codebase, lint, template):
        if self.quantum.get('ci.using') not in ('jenkins', 'gitlab+jenkins'):
            return
        project_type = str.replace(self.quantum.get('project.type'), '+', '-')
        project_name = self.quantum.get('project.name')
        template_name = f'Jenkinsfile.{project_type}.j2'
        ctx = {}
        ctx.update(lint.getlanguages())
        with codebase.commit("Compile CI/CD pipeline"):
            codebase.mkdir('ops/jenkins')
            self.assembler.notify('pipeline_render', ctx)
            print(ctx)
            template.render_to_file(f'ci/jenkins/init.{project_type}.groovy.j2',
                f'ops/jenkins/900-{project_name}.groovy', **ctx)

    def handle_configure(self, codebase, args, ci):
        if not self.spec:
            self.spec = self.schema_class.getfordump().dump()
        with self.codebase.commit("Configure Jenkins", noprefix=True):
            if args.folder:
                self.spec.jenkins.folder = str.strip(args.folder, '/')
            if args.mounted_secrets:
                secrets = []
                for secret in args.mounted_secrets:
                    kind, name, path = str.split(secret, ':')
                    secrets.append({'name': name, 'path': path})
                ci.configure({'mounted_secrets': secrets})
            self.quantum.update(self.spec)
            self.quantum.persist()

    def on_secret_loaded(self, vault, secret):
        if vault.name != 'jenkins':
            return

    def isenabled(self):
        return self.quantum.get('jenkins')
