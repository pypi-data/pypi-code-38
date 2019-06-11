
from dvcr.containers.base import BaseContainer
from dvcr.utils import wait


class Zookeeper(BaseContainer):
    def __init__(self, image="confluentinc/cp-zookeeper", tag="latest", port=2181, network=None):
        """ Constructor for Kafka """
        super(Zookeeper, self).__init__(port=port, image=image, tag=tag, network=network)

        self.port = port

        self._container = self._client.containers.run(
            image=image + ":" + tag,
            environment={
                "ZOOKEEPER_CLIENT_PORT": port,
                "ZOOKEEPER_TICK_TIME": 2000
            },
            detach=True,
            name="zookeeper",
            network=self._network.name,
        )
