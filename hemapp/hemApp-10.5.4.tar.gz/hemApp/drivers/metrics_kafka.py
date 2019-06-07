import socket
import time
import logging
import hemApp
from pykafka import KafkaClient

class instance(hemApp.Metrics):
    config = None
    server = None
    port = 9092
    client = None

    def __init__(self, config):
        self.config = config
        self.server = config.get('server', 'localhost')
        self.port = config.get('port', 9092)
        self.logger = logging.getLogger(__name__)
        self.client = KafkaClient(hosts="{}:{}".format(self.server, self.port))

    def stage(self, name, value):
        topic = self.client.topics[b'hem']
        with topic.get_sync_producer() as producer:
            producer.produce(str.encode('{} {} {}'.format(name, value, int(time.time()))))

    def store(self):
        self.logger.debug("Not implemented")
    def __del__(self):
        self.logger.debug("Not implemented")