import docker
from docker.errors import NotFound, APIError


class Network(object):
    def __init__(self, name, driver="bridge"):
        """ Constructor for Network """
        super(Network, self).__init__()

        self.name = name

        self._client = docker.from_env()

        self.network = self._client.networks.create(name=name, driver=driver)

    def delete(self):
        self.network.remove()


class DefaultNetwork(object):

    network = None

    def __init__(self, driver="bridge"):
        if not DefaultNetwork.network:
            DefaultNetwork.network = Network(name="default_network", driver=driver)

    def __getattr__(self, name):
        return getattr(self.network, name)

    def delete(self):

        try:
            self.network.delete()
        except (NotFound, APIError):
            pass
