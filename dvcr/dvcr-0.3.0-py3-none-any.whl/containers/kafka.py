from typing import Optional

from dvcr.containers.base import BaseContainer
from dvcr.containers.zookeeper import Zookeeper
from dvcr.network import Network


class Kafka(BaseContainer):
    def __init__(
        self,
        repo: str = "confluentinc/cp-kafka",
        tag: str = "latest",
        port: int = 9092,
        name: str = "kafka",
        network: Optional[Network] = None,
        zookeeper: Optional[Zookeeper] = None,
    ):
        """ Constructor for Kafka """
        super(Kafka, self).__init__(
            port=port, repo=repo, tag=tag, name=name, network=network
        )

        if zookeeper:
            self.zookeeper = zookeeper
        else:
            self.zookeeper = Zookeeper(network=network, tag=tag).wait()

        self._container = self._client.containers.run(
            image=repo + ":" + tag,
            environment={
                "KAFKA_BROKER_ID": 1,
                "KAFKA_ZOOKEEPER_CONNECT": self.zookeeper.name
                + ":"
                + str(self.zookeeper.port),
                "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:"
                + str(port),
                "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": "PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
                "KAFKA_INTER_BROKER_LISTENER_NAME": "PLAINTEXT",
                "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": 1,
            },
            detach=True,
            name=name,
            network=self._network.name,
            ports={port: port},
        )

    def create_topic(self, name, partitions=1):

        self.exec(
            cmd=[
                "kafka-topics",
                "--create",
                "--zookeeper",
                "zookeeper:2181",
                "--topic",
                name,
                "--replication-factor",
                "1",
                "--partitions",
                str(partitions),
            ]
        )

        return self

    def write_records(self, topic, key_separator=None, path_or_buf=None):

        self._logger.info("Writing records to %s", topic)

        cmd = [
            "kafka-console-producer",
            "--broker-list",
            "kafka:9092",
            "--topic",
            topic,
            "--property",
            "parse.key={}".format(bool(key_separator)).lower(),
        ]

        if key_separator:
            cmd += ["--property", "key.separator=" + key_separator]

        self.exec(cmd=cmd, path_or_buf=path_or_buf)

        return self

    def delete(self):
        self.zookeeper.delete()
        super(Kafka, self).delete()
