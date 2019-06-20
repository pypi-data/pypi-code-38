import json
from kafka import KafkaConsumer, KafkaProducer
from mcneelat.pyutils.confutils import AbstractLogUtils
from random import randint


class KafkaBuilder(AbstractLogUtils):
    """Class containing handy methods common to working with Kafka streams."""

    def __init__(self, bootstrap_servers, verbose=True):
        """
        Initialize class.
        :param bootstrap_servers: list of bootstrap servers to connect to
        """
        self.bootstrap_servers = bootstrap_servers
        AbstractLogUtils.__init__(self, verbose)

    def get_consumer(self, topic, is_json=False):
        """
        Build a Kafka consumer object.
        :param topic: topic to poll
        :param is_json: whether or not the contents of the Kafka topic are in JSON format
        :return: KafkaConsumer object
        """
        consumer_id = "%d-%s-%d" % (randint(0, 16777216), topic, randint(0, 16777216))
        self.log("[*] Initializing Kafka consumer with consumer ID: %s" % consumer_id)
        if is_json:
            consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers, client_id=consumer_id,
                                     value_deserializer=lambda m: json.loads(m.decode('ascii')))
        else:
            consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers, client_id=consumer_id)
        return consumer

    def get_producer(self, topic):
        """
        Build a Kafka producer object.
        :param topic: topic to write to
        :return: KafkaProducer object
        """
        producer_id = "%d-%s-%d" % (randint(0, 16777216), topic, randint(0, 16777216))
        self.log("[*] Initializing Kafka producer with producer ID: %s" % producer_id)
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, client_id=producer_id)
        return producer
