from qsa.ext.base import BaseExtension


class Extension(BaseExtension):
    name = inject = command_name = 'ops'

    def setdeploymentframework(self, framework):
        """Configures the deployment framework e.g. Ansible, Chef.
        Supported values are: ``ansible``.
        """
        self.spec.ops.using = framework

    def getenvironments(self):
        """Return a sequence holding objects representing the
        deployment environments.
        """
        return list(self.quantum.get('deployment.environments').values())
