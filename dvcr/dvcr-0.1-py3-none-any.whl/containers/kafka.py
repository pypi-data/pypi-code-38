
from dvcr.containers.base import BaseContainer
from dvcr.containers.zookeeper import Zookeeper


class Kafka(BaseContainer):

    def __init__(self, image="confluentinc/cp-kafka", tag="latest", port=9092, network=None, zookeeper=None):
        """ Constructor for Kafka """
        super(Kafka, self).__init__(port=port, image=image, tag=tag, network=network)

        if zookeeper:
            self.zookeeper = zookeeper
        else:
            self.zookeeper = Zookeeper(network=network, tag=tag).wait()

        self._container = self._client.containers.run(
            image=image + ":" + tag,
            environment={
                "KAFKA_BROKER_ID": 1,
                "KAFKA_ZOOKEEPER_CONNECT": self.zookeeper.name + ":" + str(self.zookeeper.port),
                "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:" + str(port),
                "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": "PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
                "KAFKA_INTER_BROKER_LISTENER_NAME": "PLAINTEXT",
                "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": 1,
            },
            detach=True,
            name="kafka",
            network=self._network.name,
            ports={port: port}
        )

    def create_topic(self, name, partitions):

        exit_code, output = self._container.exec_run(
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
                partitions,
            ],
            tty=True,
        )

        print(output)

        return self

    def write_records(self, topic, source_file_path, key_separator="|"):

        socket = self._container.exec_run(
            cmd=[
                "kafka-console-producer",
                "--broker-list",
                "kafka:9092",
                "--topic",
                topic,
                "--property",
                "parse.key=true",
                "--property",
                "key.separator=" + key_separator
            ],
            socket=True,
            stdin=True,
        ).output

        with open(source_file_path, "rb") as _file:
            socket.sendall(_file.read())
            socket.close()

        return self

    def delete(self):
        self.zookeeper.delete()
        self._container.stop()
        self._container.remove()
