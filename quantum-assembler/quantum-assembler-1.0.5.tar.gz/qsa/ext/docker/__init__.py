import os

from qsa.ext.base import BaseExtension
from qsa import const
from qsa.spec import QuantumSpecification

from .schema import ConfigSchema
from .schema import ContainerConfigSchema


class Extension(BaseExtension):
    name = command_name = 'docker'
    schema_class = ConfigSchema
    subcommands = [
        {
            'name': 'configure',
            'args': [
                ('--registry', {}),
                ('--repository', {}),
            ]
        },
        {
            'name': 'containerize',
            'args': []
        },
        {
            'name': 'init',
            'args': [
                {'dest': 'base'},
                {'dest': 'name'},
                ('--registry', {'default': 'docker.io'}),
                ('--with-ci', {'dest': 'ci'})
            ]
        }
    ]
    weight= 10.0

    def handle_configure(self, args, codebase):
        if args.registry:
            with codebase.commit("Configure container registry"):
                self.spec.docker.registry = args.registry
                self.quantum.update(self.spec)
                self.quantum.persist(codebase)
        if args.repository:
            with codebase.commit("Configure container repository"):
                self.spec.docker.repository = args.repository
                self.quantum.update(self.spec)
                self.quantum.persist(codebase)

    def can_handle(self, codebase):
        return codebase.exists('Dockerfile')

    def get_default_config(self):
        return {
            'docker': {
                'repository': self.quantum.get('project.name')\
                    or os.getenv('QSA_PROJECT_NAME') or None
            }
        }

    def handle(self, codebase):
        if not self.quantum.get('docker', None)\
        or not codebase.exists('Dockerfile'):
            return
        with codebase.commit("Containerize using Docker"):
            if not codebase.exists('.hadolint.yaml'):
                self.render_to_file(codebase, 'hadolint.yml.j2',
                    '.hadolint.yaml')

    def handle_containerize(self, codebase, ci):
        self.edit(codebase, new=True)

    def handle_init(self, args, codebase, ci):
        assert args.name
        schema = self.schema_class.getforload()
        _, project_name = str.rsplit(args.name, '/', 1)
        with codebase.commit("Create Docker image project"):
            self.quantum.init('container-image', project_name,
                codebase=codebase)
            self.spec = schema.load({
                'docker': {
                    'registry': args.registry,
                    'repository': args.name
                }
            })
            ctx = {
                'DOCKER_BASE_IMAGE': args.base
            }
            if not codebase.exists('Dockerfile'):
                self.render_to_file(codebase, 'Dockerfile.base.j2',
                    'Dockerfile', ctx=ctx)
            self.quantum.update({'docker': self.spec})
            if args.ci:
                assert args.ci == 'jenkins'
                ci.configure({
                    'using': args.ci,
                    'strategy': 'trunk+tagged'
                })

                # Set the registry provided on the command-line as the
                # default for publishing.
                self.quantum.spec['ci']['container_registries']['publish']['url'] = f'https://{args.registry}'

            self.quantum.persist(codebase)

    def on_setup_makefile(self, mk):
        """Adds the common QSA Makefile targets."""
        if not self.quantum.get('docker', None):
            return

        mk.target('docker-image')
        mk.target('docker-push')
        mk.target('docker-publish')
        #mk.target('docker-image-local')
        #mk.target('docker-push-local')
        #mk.target('docker-publish-local')
        mk.target('docker-lint')
        mk.setvariable('DOCKER_TMPNAME',
            "$(GIT_COMMIT_HASH)")
        mk.setvariable('DOCKER_REGISTRY',
            self.quantum.get('docker.registry'), export=True)
        mk.setvariable('DOCKER_REPOSITORY',
            self.quantum.get('docker.repository'))
        mk.setvariable('DOCKER_QUALNAME',
            '$(DOCKER_REGISTRY)/$(DOCKER_REPOSITORY)', export=True)
        mk.setvariable('DOCKER_IMAGE_QUALNAME',
            '$(DOCKER_REGISTRY)/$(DOCKER_REPOSITORY):$(IMAGE_TAG)', export=True)
        #mk.setvariable('DOCKER_LOCAL_REGISTRY',
        #    const.QUANTUM_DOCKER_REGISTRY)
        #mk.setvariable('QSA',
        #    "docker run -it -v $${pwd}:/app -w /app quantumframework/qsa:latest")

    def on_setup_makefile_target_docker_image(self, make, target):
        target.execute('docker build -t $(DOCKER_TMPNAME) .')
        target.execute('docker tag $(DOCKER_TMPNAME) $(DOCKER_QUALNAME):$(IMAGE_TAG)')
        target.execute('docker tag $(DOCKER_TMPNAME) $(DOCKER_QUALNAME):latest')
        target.execute('docker image rm -f $(DOCKER_TMPNAME)')

    def on_setup_makefile_target_docker_push(self, make, target):
        target.execute('docker push $(DOCKER_QUALNAME):$(IMAGE_TAG)')
        target.execute('docker push $(DOCKER_QUALNAME):latest')

    def on_setup_makefile_target_docker_publish(self, make, target):
        target.execute('make docker-image')
        target.execute('make docker-push')

    #def on_setup_makefile_target_docker_image_local(self, make, target):
    #    target.execute(f'make docker-image DOCKER_REGISTRY=$(DOCKER_LOCAL_REGISTRY)')

    #def on_setup_makefile_target_docker_push_local(self, make, target):
    #    target.execute(f'make docker-push DOCKER_REGISTRY=$(DOCKER_LOCAL_REGISTRY)')

    #def on_setup_makefile_target_docker_publish_local(self, make, target):
    #    target.execute(f'make docker-publish DOCKER_REGISTRY=$(DOCKER_LOCAL_REGISTRY)')

    def on_setup_makefile_target_docker_lint(self, make, target):
        target.execute("docker run --rm -v $(pwd):/app -w /app\\\n\t -i hadolint/hadolint < Dockerfile")
