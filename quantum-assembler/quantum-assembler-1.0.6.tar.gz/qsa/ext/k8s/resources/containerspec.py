import abc

from .container import Container


class ContainerSpec(abc.ABC):
    containers = abc.abstractproperty()

    def getcontainer(self, qualname):
        """Return a container by its name."""
        for container in self.containers:
            if container.name != qualname:
                continue
            break
        else:
            raise LookupError(f'No such container: {qualname}')
        return Container(container)
