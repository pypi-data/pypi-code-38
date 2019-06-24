from typing import Optional

from dvcr.containers.base import BaseContainer
from dvcr.network import Network


class Redis(BaseContainer):
    def __init__(
        self,
        repo: str = "redis",
        tag: str = "5",
        port: int = 6379,
        name: str = "redis",
        network: Optional[Network] = None,
    ):
        """ Constructor for Redis """
        super(Redis, self).__init__(
            port=port, repo=repo, tag=tag, name=name, network=network
        )

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            detach=True,
            name=name,
            network=self._network.name,
            ports={port: port},
        )

    def set(self, key, value):

        self.exec(cmd=["redis-cli", "set", key, value])

        return self

    def sql_alchemy_conn(self, dialect="redis", driver=None):

        dialect_driver = dialect

        if driver:
            dialect_driver = dialect_driver + "+" + driver

        return "{dialect_driver}://{host}:{port}/{db}".format(
            dialect_driver=dialect_driver,
            host=self._container.name,
            port=self.port,
            db=0,
        )
