import json
from kafka import KafkaConsumer, KafkaProducer
from random import randint


class KafkaBuilder:
    def __init__(self, bootstrap_servers, topic):
        self.bootstrap_servers = bootstrap_servers

    def get_consumer(self, topic, is_json=False):
        consumer_id = "%d-%s-%d" % (randint(0, 16777216), topic, randint(0, 16777216))
        print("[*] Initializing Kafka consumer with consumer ID: %s" % consumer_id)
        if is_json:
            consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers, client_id=consumer_id,
                                     value_deserializer=lambda m: json.loads(m.decode('ascii')))
        else:
            consumer = KafkaConsumer(topic, bootstrap_servers=self.bootstrap_servers, client_id=consumer_id)
        return consumer

    def get_producer(self, topic):
        producer_id = "%d-%s-%d" % (randint(0, 16777216), topic, randint(0, 16777216))
        print("[*] Initializing Kafka producer with producer ID: %s" % producer_id)
        producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, client_id=producer_id)
        return producer
