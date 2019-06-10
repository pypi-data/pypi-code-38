from .utils.event_hook import EventHook
from .options.test_bed_options import TestBedOptions
from .kafka.consumer_manager import ConsumerManager
from .kafka.producer_manager import ProducerManager
from .registry.schema_registry import SchemaRegistry
from .registry.schema_publisher import SchemaPublisher
from .kafka.heartbeat_manager import HeartbeatManager
from .services.time_service import TimeService
from pykafka.connection import SslConfig
import logging


class TestBedAdapter:
    def __init__(self, test_bed_options: TestBedOptions):

        self.test_bed_options = test_bed_options
        self.schema_registry = SchemaRegistry(test_bed_options)
        self.schema_publisher = SchemaPublisher(test_bed_options)
        self.default_producer_topics = ["system_heartbeat"]
        self.default_consumer_topics = ["system_timing"]
        self.consumer_managers = {}
        self.producer_managers = {}
        self.connected = False
        self.heartbeat_manager: HeartbeatManager = None
        self.time_service: TimeService = None

        # If we are using ssl we create the ssl config object
        if self.test_bed_options.use_ssl:
            self.ssl_config = SslConfig(self.test_bed_options.ca_file, self.test_bed_options.cert_file,
                                        self.test_bed_options.key_file, self.test_bed_options.password_private_key)
        else:
            self.ssl_config = None

        # We set up the handlers for the events
        self.on_ready = EventHook()
        self.on_message = EventHook()
        self.on_sent = EventHook()
        self.on_error = EventHook()

    def initialize(self):
        logging.info("Initializing test bed")
        self.schema_publisher.start_process()
        self.schema_registry.start_process()
        self.init_consumers()
        self.init_producers()
        self.init_and_start_heartbeat()
        self.init_services()
        self.connected = True

        # We emit here by firing the on ready observable.
        self.on_ready.fire()

    def init_consumers(self):
        # Make sure default topics are considered, avoid duplicates
        self.test_bed_options.consume = list(set(self.test_bed_options.consume + self.default_consumer_topics))

        # Instantiate one consumer manager for each topic
        for topic_name in self.test_bed_options.consume:
            if topic_name in list(self.schema_registry.values_schema.keys()):
                avro_helper_key = self.schema_registry.keys_schema[topic_name]["avro_helper"]
                avro_helper_value = self.schema_registry.values_schema[topic_name]["avro_helper"]

                # We create a new consumer for this topic. The last input is the callback
                # where we handle the message received and decoded from kafka.
                manager = ConsumerManager(bytes(topic_name, 'utf-8'),
                                          self.test_bed_options.kafka_host,
                                          self.test_bed_options.exclude_internal_topics,
                                          self.test_bed_options.reset_offset_on_start,
                                          self.test_bed_options.offset_type,
                                          self.test_bed_options.client_id,
                                          avro_helper_key,
                                          avro_helper_value,
                                          self.handle_message,
                                          self.ssl_config)
                self.consumer_managers[topic_name] = manager
                logging.info("Initialized kafka consumer manager for topic " + topic_name)
            else:
                logging.error("No schema found for topic " + topic_name)

    def init_producers(self):
        # Make sure default topics are considered, avoid duplicates
        self.test_bed_options.produce = list(set(self.test_bed_options.produce + self.default_producer_topics))

        # Instantiate one producer manager for each topic
        for topic_name in self.test_bed_options.produce:
            if topic_name in list(self.schema_registry.values_schema.keys()):
                avro_helper_key = self.schema_registry.keys_schema[topic_name]["avro_helper"]
                avro_helper_value = self.schema_registry.values_schema[topic_name]["avro_helper"]

                # We create a new producer for this topic. The last input is the callback
                # where we handle the message sent.
                manager = ProducerManager(bytes(topic_name, 'utf-8'), self.test_bed_options.kafka_host,
                                          self.test_bed_options.exclude_internal_topics,
                                          self.test_bed_options.client_id,
                                          self.test_bed_options.send_messages_asynchronously,
                                          avro_helper_key, avro_helper_value,
                                          self.successfully_sent_message, self.ssl_config)
                self.producer_managers[topic_name] = manager
                logging.info("Initialized kafka producer manager for topic" + topic_name)
            else:
                logging.error("No schema found for topic " + topic_name)

    def init_services(self):
        if "system_timing" not in self.consumer_managers.keys():
            logging.error("TimeService could not be initialized, No schema found for topic system_timing")
        else:
            self.time_service = TimeService(self.consumer_managers["system_timing"])

    def init_and_start_heartbeat(self):
        if "system_heartbeat" in self.producer_managers.keys():
            self.heartbeat_manager = HeartbeatManager(self.producer_managers["system_heartbeat"],
                                                      self.test_bed_options.heartbeat_interval,
                                                      self.test_bed_options.client_id)
            self.heartbeat_manager.start_heartbeat_async()
        else:
            logging.error("Heartbeat could not be initialized, No schema found for topic system_heartbeat")

    def stop(self):
        # Stop the heartbeat thread
        if self.heartbeat_manager is not None:
            self.heartbeat_manager.stop()
        # Stop all the kafka listeners
        for manager in list(self.consumer_managers.values()):
            manager.stop()
        for manager in list(self.producer_managers.values()):
            manager.stop()
        # Stop time service
        if self.time_service is not None:
            self.time_service.stop()
        self.connected = False

    def handle_message(self, message):
        # We emit the message recieved
        self.on_message.fire(message)

    def successfully_sent_message(self, message):
        # We emit the message sent
        self.on_sent.fire(message)
