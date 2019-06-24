from typing import Optional

from dvcr.containers.base import BaseContainer
from dvcr.network import Network


class RabbitMQ(BaseContainer):
    def __init__(
        self,
        repo: str = "rabbitmq",
        tag: str = "3.7.15",
        port: int = 5672,
        name: str = "rabbitmq",
        network: Optional[Network] = None,
    ):
        """ Constructor for RabbitMQ """
        super(RabbitMQ, self).__init__(
            port=port, repo=repo, tag=tag, name=name, network=network
        )

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name,
            network=self._network.name,
            ports={port: port},
        )

    def sql_alchemy_conn(self, dialect="amqp", driver=None):

        dialect_driver = dialect

        if driver:
            dialect_driver = dialect_driver + "+" + driver

        return "{dialect_driver}://{user}:{pwd}@{host}:{port}/{db}".format(
            dialect_driver=dialect_driver,
            user="guest",
            pwd="guest",
            host=self._container.name,
            port=self.port,
            db="",
        )
