from ..schema import EnvironmentConfigSchema


class DeploymentManager:
    """Maintains information about all deployments declared by the
    current Quantum project.
    """

    def __init__(self):
        self._runtimes = {}

    def createruntime(self, name, withenv=True):
        """Creates a new runtime of the application image."""
        assert name not in self._runtimes
        self._runtimes[name] = runtime = Runtime(name)
        return runtime

    def create(self, name, group=None, development=False, image=None, withenv=False):
        """Create a new :class:`Deployment`."""
        if not withenv:
            withenv = image is not None



class Runtime:
    """Represents a runtime instance of the application code with
    a specific environment configuration.
    """

    def __init__(self, name):
        self._name = name


class Deployment:
    """Represents a runtime instance of the application code with
    a specific environment configuration.
    """
    schema = EnvironmentConfigSchema()

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(**cls.schema.defaults(*args, **kwargs))

    def __init__(self, name, annotations=None, alias=None, production=False, purgeable=False):
        self.name = name
        self.alias = alias
        self.annotations = annotations or {}
        self.production = production
        self.purgeable = purgeable

    def dump(self):
        """Dumps the :class:`Deployment` to a dictionary."""
        return self.schema.dump(self)

    def annotate(self, domain, name, value):
        """Creates or updates an annotation for this environment."""
        pass

    def setproduction(self, mode):
        """Sets the production mode for this environment."""
        self.production = bool(mode)
