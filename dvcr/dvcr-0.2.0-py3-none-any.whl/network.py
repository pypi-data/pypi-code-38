import uuid

import docker
from docker.errors import NotFound, APIError

from dvcr.utils import init_logger, bright


class Network(object):
    def __init__(self, name, driver="bridge"):
        """ Constructor for Network """
        super(Network, self).__init__()

        self.logger = init_logger(name="network")

        self.name = name

        client = docker.from_env()

        self.network = client.networks.create(name=name, driver=driver)

        self.logger.info("Created network %s", bright(string=name))

    def delete(self):
        try:
            self.network.remove()
            self.logger.info("Deleted network %s ♻", bright(string=self.name))
        except APIError as e:
            if e.status_code == 403:
                self.logger.warn(
                    "Could not delete network %s. It is used by an active container",
                    bright(string=self.name),
                )
            else:
                raise e


class DefaultNetwork(object):

    network = None

    def __init__(self, driver: str = "bridge"):
        if not DefaultNetwork.network:
            DefaultNetwork.network = Network(
                name=self._generate_network_name(), driver=driver
            )

    def __getattr__(self, name):
        return getattr(self.network, name)

    @staticmethod
    def _generate_network_name() -> str:
        return "dvcr_network_" + (uuid.uuid4().hex[:8])

    def delete(self):

        try:
            self.network.delete()
        except (NotFound, APIError):
            pass

    def __del__(self):
        self.delete()
