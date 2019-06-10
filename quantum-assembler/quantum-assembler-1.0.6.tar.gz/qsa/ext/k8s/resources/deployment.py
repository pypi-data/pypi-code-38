from qsa.lib.datastructures import DTO
from .base import Resource
from .container import Container
from .containerspec import ContainerSpec
from .prefixable import Prefixable
from .persistable import Persistable


class Deployment(Resource, Prefixable, Persistable, ContainerSpec):
    api_version = 'apps/v1'
    kind = 'Deployment'
    group = 'deployments'
    stage = 'applications'

    @property
    def containers(self):
        return self.template_spec.setdefault('containers', [])

    @property
    def selector(self):
        return self.template_metadata.labels

    @property
    def template_spec(self):
        return self.template.setdefault('spec', DTO())

    @property
    def template_metadata(self):
        return self.template.setdefault('metadata', DTO())

    @property
    def template(self):
        return self.spec.setdefault('template', DTO())

    @property
    def spec(self):
        return self._manifest.setdefault('spec', DTO())

    def addtoservice(self, svc):
        """Configures the service `svc` to forward traffic to the
        :class:`Deployment`.
        """
        for k, v in self.selector.items():
            svc.setselector(k, v)

    def createcontainer(self, image, name):
        """Create a new container in the :class:`Deployable`."""
        self.containers.append(Container(DTO(image=image, name=name)))
        return self.containers[-1]

    def setreplicas(self, num):
        self.spec.replicas = num

    def setselector(self, selector):
        self.spec.selector = {
            'matchLabels': selector
        }
        self.template_metadata.labels = selector

    def setserviceaccount(self, name):
        """Sets the service account for the created ``Pod``."""
        self.template_spec.serviceAccountName = name
