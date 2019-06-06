import ioc

from qsa.ext.base import BaseExtension

from .schema import ConfigSchema
from .model import Deployment


class Extension(BaseExtension):
    name = command_name = inject = 'deployment'
    schema_class = ConfigSchema
    weight = 10.0
    project_types = [
        'k8s+cluster'
    ]

    def setup_injector(self, injector):
        super().setup_injector(injector)
        self.provide_class(self)

    def getalias(self, name):
        """Return the alias for the given environment,
        or the environment name.
        """
        env = self.getenv(name)
        if env is None:
            raise ValueError(f"No such environment: {name}")
        return env.alias or env.name

    def getenv(self, name):
        """Return a datastructure containing the environment
        specification, or ``None`` if it does not exist.
        """
        for env in self.spec.deployment.environments.values():
            if not env.alias == name and not env.name == name:
                continue
            break
        else:
            env = None
        return env

    def getall(self):
        return self.spec.deployment.environments.values()

    def isenabled(self):
        """Return a boolean indicating if the extension configured
        should be included in the ``Quantumfile``.
        """
        return self.isprojectsupported()\
            or self.quantum.get('deployment', None)

    def isprojectsupported(self):
        """Return a boolean indicating if this extensions supported
        the project type.
        """
        return self.quantum.get('project.type') in self.project_types

    def createenv(self, name, alias=None, isproduction=False, allow_purge=False):
        """Gets or creates a new deployment environment."""
        env = self.spec.deployment.environments.get(name)
        if env:
            self.fail(f"Environment already exists: {name}")
        env = self.spec.deployment.environments[name] = Deployment.new({
            'name': name,
            'alias': alias,
            'production': isproduction,
            'purgeable': allow_purge
        })
        return env, True

    def on_vaults_init(self, codebase, secrets, vaults):
        """Create a vault for each environment if it does not
        exist.
        """
        for name, env in dict.items(self.spec.deployment.environments):
            if vaults.exists(name):
                continue
            vaults.create(codebase, name)

    def on_template_render(self, ctx):
        ctx.update({
            'DEPLOYMENT_ENVIRONMENTS': list(self.quantum.get('deployment.environments', {})\
                .values())
        })
        ctx['DEPLOYMENT_ENVIRONMENTS'].append({
            'name': 'global',
            'display_name': 'global'
        })
