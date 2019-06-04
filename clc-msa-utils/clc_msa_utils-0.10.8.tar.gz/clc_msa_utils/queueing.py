import datetime
import json
import logging
import random
import threading
import traceback

import pika

from clc_msa_utils.kv_store import KVStore
from clc_msa_utils.log_manager import LogManager


class QueueConsumer:

    def __init__(self, config={}):
        self._config = {}
        self._logger = logging.getLogger('QueueConsumer')
        self._connection = None
        self._channel = None
        self._callback = None
        self._worker_thread = None
        self._stop_consuming = False

        self._config = config

    def _configure_listener(self):
        if 'auth' not in self._config \
                or 'user' not in self._config['auth'] \
                or 'password' not in self._config['auth'] \
                or 'queue' not in self._config \
                or 'host' not in self._config \
                or 'port' not in self._config:
            self._logger.error("config=" + str(self._config))
            raise Exception("Expected the consumer configuration to have an auth.user, "
                            "auth.password, host, queue, and port attribute, but received: {0}"
                            .format(str(self._config)))
        credentials = pika.PlainCredentials(self._config['auth']['user'], self._config['auth']['password'])
        parameters = pika.ConnectionParameters(self._config['host'], int(self._config['port']), '/', credentials)
        self._logger.debug("Creating connection.")
        self._connection = pika.BlockingConnection(parameters)
        if not self._stop_consuming:
            self._logger.debug("Creating channel.")
            self._channel = self._connection.channel()
            self._logger.debug("Declaring queue.")
            self._channel.queue_declare(queue=self._config['queue'], durable=True)

            if 'exchange' in self._config:
                self._channel.queue_bind(queue=self._config['queue'], exchange=self._config['exchange']['name'],
                                         routing_key=self._config['binding_key'])

            self._logger.debug("Set listener on queue {0}."
                               .format(self._config['queue']))
            self._channel.basic_qos(prefetch_count=1)
            self._channel.basic_consume(self._callback, queue=self._config['queue'])

            self._logger.debug("Start consuming on queue {0}."
                               .format(self._config['queue']))
            self._channel.start_consuming()

    def get_config(self):
        return self._config

    def listen(self, callback, blocking=True):
        self._callback = callback

        if blocking:
            self._logger.debug("Creating blocking listener.")
            self._configure_listener()
        else:
            self._logger.debug("Creating non-blocking listener.")
            self._worker_thread = threading.Thread(target=self._configure_listener)
            self._worker_thread.start()

    def stop_consuming(self):
        self._stop_consuming = True
        try:
            if not self._channel:
                self._logger.debug("Channel has not start consuming yet.".format(self._config.get('name')))
                return
            if not self._channel.is_closed:
                try:
                    self._channel.stop_consuming()
                    self._logger.debug("Channel stopped consuming on '{0}' thread.".format(self._config.get('name')))
                except:
                    self._logger.warning(traceback.format_exc())
                    self._logger.warning("Channel wouldn't stop consuming on '{0}' thread, closing channel.".format(
                        self._config.get('name')))
                    self._channel.close()
        except:
            self._logger.error(traceback.format_exc())

    def thread(self):
        return self._worker_thread

    def config(self):
        return self._config

    def callback(self):
        return self._callback


class QueueProducer:

    def __init__(self, config={}):
        self._config = {}
        self._logger = logging.getLogger('QueueProducer')
        self._connection = None
        self._queue_channel = None
        self._config = self._normalize_config(config)
        self._configure_producer()

    def _configure_producer(self):
        self._logger.debug("Configuring queue producer with config:\n%s" % self._config)
        if not self._connection or self._connection.is_closed:
            credentials = pika.PlainCredentials(self._config['auth']['user'], self._config['auth']['password'])
            parameters = pika.ConnectionParameters(self._config['host'], int(self._config['port']), '/', credentials)
            self._connection = pika.BlockingConnection(parameters)
        if not self._queue_channel or self._queue_channel.is_closed:
            self._queue_channel = self._connection.channel()

            if 'create' in self._config['exchange'] and self._config['exchange']['create']:
                self._logger.debug("Exchange is being ensured present based on configuration...")
                self._queue_channel \
                    .exchange_declare(exchange=self._config['exchange']['name'],
                                      exchange_type=(
                                          self._config['exchange']['type'] if 'type' in self._config[
                                              'exchange'] else 'direct'),
                                      arguments=(self._config['exchange']['arguments'] if 'arguments' in
                                                                                          self._config[
                                                                                              'exchange'] else {}),
                                      durable=(
                                          self._config['exchange']['durable'] if 'durable' in self._config[
                                              'exchange'] else True))

    def _normalize_config(self, config):
        return config

    def publish(self, message=None, properties=None, try_number=0):
        try_number = try_number + 1

        self._logger.info("Publishing message to exchange '{0}' with binding key '{1}'"
                          .format(self._config['exchange']['name'],
                                  self._config['binding_key']))
        self._configure_producer()

        if type(message) is dict:
            body = json.dumps(message)
        else:
            body = str(message)

        self._logger.debug("Message:\n%s" % body)

        if not properties:
            properties = pika.BasicProperties()

        # Make message persistent
        properties.delivery_mode = 2
        # Assume json
        properties.content_type = 'application/json'

        if self._connection.is_closed or self._queue_channel.is_closed:
            self._configure_producer()

        try:
            self._queue_channel.basic_publish(exchange=self._config['exchange']['name'],
                                              routing_key=(
                                                  self._config[
                                                      'binding_key'] if 'binding_key' in self._config else '#'),
                                              body=body,
                                              properties=properties)
            self._logger.info("SUCCESS: Message Published")
        except Exception as e:
            if try_number > 5:
                raise e
            else:
                self._logger.info("FAILED: An error occurred publishing to the {0} exchange with binding key {1},"
                                  " retrying. This is try number {2}."
                                  .format(self._config['exchange']['name'],
                                          self._config['binding_key'] if 'binding_key' in self._config else '#',
                                          str(try_number)))
                self._configure_producer()
                self.publish(message=message, properties=properties, try_number=try_number)

    def get_config(self):
        return self._config


class QueueFactory:
    """
    QueueFactory provides helper methods for simply passing in a configuration
    and having producers/consumers created based on that config.  Additionally,
    there will be builder style methods available for setting/overriding configuration
    prior to generating producers/consumers.

    Currently, this solution is satisfying making a connection using AMQP which is compatible with
    RabbitMQ and ActiveMQ.  It could be enhanced to provide further abstraction and provide
    connections to other Queue services in theory.
    """

    _logger = logging.getLogger('QueueFactory')

    def __init__(self, monitoring_period_seconds=10):
        self._consumers = {}
        self._producers = {}
        self._config = {}
        self._monitoring = False
        self._monitoring_period_seconds = monitoring_period_seconds
        self._monitoring_thread = None
        self._logger.info("Initializing QueueFactory...")

    def create_consumers(self, queue_config):
        """
        Example Consumer Queue Configuration:
        {
          "queue_config": [
            {
              "name": "name-to-reference-this-connection",
              "type": "consumer",
              "exchange": {
                "name": "name-of-exchange",
                "type": "direct | fanout | etc",
                "arguments": {"x-delayed-type": "topic"},
                "durable": true | false
              },
              "queue": "name-of-queue",
              "binding_key": "#",
              "host": "rabbitmq-host",
              "port": "5672",
              "auth": {
                "user": "guest",
                "password": "guest"
              }
            }
          ]
        }
        """

        if 'queue_config' in queue_config:
            queue_config = queue_config['queue_config']

        self._logger.debug("Setting up consumers for the following configuration:\n%s" % str(queue_config))
        for config in queue_config:
            if 'type' in config and 'consumer' == config['type']:
                consumer = QueueConsumer(config)
                self._logger.debug("Adding configuration for configuration %s." % str(config['name']))
                self._consumers[config['name']] = consumer

        self._logger.debug("Created {0} consumers.".format(str(len(self._consumers))))
        for consumer in list(self._consumers.values()):
            self._logger.debug("Created {0} consumer.".format(consumer.config().get("name")))
        return self._consumers

    def create_producers(self, queue_config):
        """
        Example Producer Queue Configuration:
        {
            "queue_config": [
                {
                    "name": "name-to-reference-this-connection",
                    "type": "producer",
                    "exchange": {
                        "name": "name-of-exchange",
                        "create": true | false (whether or not to ensure exchange is present),
                        "type": "direct | fanout | etc",
                        "arguments": {"x-delayed-type": "topic"},
                        "durable": true | false
                    },
                    "binding_key": "#",
                    "host": "rabbitmq-host",
                    "port": "5672",
                    "auth": {
                        "user": "guest",
                        "password": "guest"
                    }
                }
            ]
        }
        """

        self._logger.debug("Setting up producers for the following configuration:\n%s" % queue_config)
        if 'queue_config' in queue_config:
            queue_config = queue_config['queue_config']

        for config in queue_config:
            if 'type' in config['exchange'] and 'producer' == config['exchange']['type']:
                producer = QueueProducer(config)
                self._producers[config['name']] = producer

        return self._producers

    def stop_consuming(self):
        """
        Stops all QueueConsumers from consuming.
        """
        self.stop_monitoring()

        for consumer in list(self._consumers.values()):
            consumer.stop_consuming()

        for consumer in list(self._consumers.values()):
            consumer.stop_consuming()
        self._consumers = {}

    def start_consuming(self, callback):
        """
        Starts all QueueConsumers consuming in a separate thread.
        """
        for consumer in list(self._consumers.values()):
            consumer.listen(callback, blocking=False)
            consumer.thread().name = "WorkerThread-{0}-{1}" \
                .format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        self._random_string())
        self.start_monitoring()

    def consumers(self):
        """
        Gets a list of all QueueConsumers

        :return: list of QueueConsumers
        """
        return list(self._consumers.values())

    def start_monitoring(self):
        self._logger.debug("Thread Monitoring Enabled checking threads every {0} seconds."
                           .format(self._monitoring_period_seconds))
        self._monitoring = True
        self._monitoring_thread = threading.Timer(self._monitoring_period_seconds, self._monitor)
        self._logger.debug("Created monitoring thread named {0}."
                           .format(self._monitoring_thread.name))
        self._monitoring_thread.start()
        self._monitoring_thread.name = "MonitorThread-{0}-{1}" \
            .format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    self._random_string())

        self._logger.debug("Monitoring thread started and is alive? {0}."
                           .format(str(self._monitoring_thread.is_alive())))

    def _random_string(self):
        return str(random.randrange(0, 999999)).zfill(6)

    def monitoring_thread(self):
        return self._monitoring_thread

    def stop_monitoring(self):
        self._logger.debug("Thread Monitoring Disabled")
        self._monitoring = False

    def _monitor(self):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Monitoring {0} threads..."
                               .format(str(len(list(self._consumers.values())))))
            self._logger.debug("There are currently {0} active threads in the system."
                               .format(str(threading.active_count())))
            for thread in threading.enumerate():
                self._logger.debug("Thread [{0}] is alive.".format(thread.name))
        if self._monitoring:
            for consumer in list(self._consumers.values()):
                if not self._monitoring:
                    break
                if not consumer.thread().is_alive():
                    consumer.listen(consumer.callback(), blocking=False)
                    self._logger.debug("Consumer thread {0} was not alive, successfully started"
                                       .format(consumer.config().get("name")))
                else:
                    self._logger.debug("Consumer thread {0} is still active."
                                       .format(consumer.config().get("name")))

        if self._monitoring:
            self.start_monitoring()
        self._logger.debug("Done monitoring threads.")


class QueueWorker:
    """
        Helper class to make writing queue workers easy. Specify kv store connection info,
        keys to retrieve configuration from the kv_store for the queue connection and initialization,
        and write your listener method. This class creates a KVStore and LogManager for you.
    """

    _logger = logging.getLogger("QueueWorker")

    def __init__(self,
                 consul_host=None,
                 consul_port=None,
                 etcd_host=None,
                 etcd_port=None,
                 kv_prefix=None,
                 rabbit_host_key="rabbit_host",
                 rabbit_port_key="rabbit_port",
                 rabbit_user_key="rabbit_user",
                 rabbit_password_key="rabbit_password",
                 amqp_connection_key="amqp_connections",
                 queue_name_key="queue_name",
                 listen_exchange_key="exchange",
                 listen_routing_key_key="listen_routing_key",
                 done_exchange_key="done_exchange",
                 done_routing_key_key="done_routing_key",
                 error_exchange_key="error_exchange",
                 error_routing_key_key="error_routing_key",
                 initialize_log_manager=True,
                 kv_store=None,
                 data_key_on_error_payload="data",

                 rabbit_host_default="localhost",
                 rabbit_port_default="5672",
                 rabbit_user_default="guest",
                 rabbit_password_default="guest",
                 queue_name_default="default_queue",
                 amqp_connection_default="10",
                 listen_exchange_default="main_exchange",
                 listen_routing_default="listen.key",
                 done_exchange_default="main_exchange",
                 done_routing_key_default="done.key",
                 error_exchange_default="error_exchange",
                 error_routing_key_default="error.key"):

        # Initialize instance variables.
        self._consul_host = consul_host
        self._consul_port = consul_port
        self._etcd_host = etcd_host
        self._etcd_port = etcd_port
        self._kv_prefix = kv_prefix

        # RabbitMQ connection, exchange, queue, and binding key KVStore keys
        self._rabbit_host_key = rabbit_host_key
        self._rabbit_port_key = rabbit_port_key
        self._rabbit_user_key = rabbit_user_key
        self._rabbit_password_key = rabbit_password_key
        self._amqp_connection_key = amqp_connection_key
        self._listen_exchange_key = listen_exchange_key
        self._queue_name_key = queue_name_key
        self._listen_routing_key_key = listen_routing_key_key
        self._done_exchange_key = done_exchange_key
        self._done_routing_key_key = done_routing_key_key
        self._error_exchange_key = error_exchange_key
        self._error_routing_key_key = error_routing_key_key
        self._error_original_payload_key = data_key_on_error_payload

        # RabbitMQ default values
        self._rabbit_host_default = rabbit_host_default
        self._rabbit_port_default = rabbit_port_default
        self._rabbit_user_default = rabbit_user_default
        self._rabbit_password_default = rabbit_password_default
        self._queue_name_default = queue_name_default
        self._amqp_connection_default = amqp_connection_default
        self._listen_exchange_default = listen_exchange_default
        self._listen_routing_default = listen_routing_default
        self._done_exchange_default = done_exchange_default
        self._done_routing_key_default = done_routing_key_default
        self._error_exchange_default = error_exchange_default
        self._error_routing_key_default = error_routing_key_default

        # Other private variables
        self._callback = None
        self._done_producer = None
        self._error_producer = None
        self._queue_factory = None

        if kv_store:
            self._kv_store = kv_store
        else:
            self._kv_store = KVStore(
                consul_host=consul_host,
                consul_port=consul_port,
                etcd_host=etcd_host,
                etcd_port=etcd_port,
                kv_prefix=kv_prefix,
                reload_enabled=True
            )

        if initialize_log_manager:
            self._log_manager = LogManager(kv_store=self._kv_store)

        self._logger.info("QueueWorker initialized.")

    def kv_store(self):
        """
            Returns the KVStore created by this class.
            :return: KVStore
        """
        return self._kv_store

    def set_callback(self, callback):
        """
            Sets the callback for the queue worker, and starts consuming
            :param callback:
        """
        self._logger.info("Setting callback...")
        self._callback = callback
        self._kv_store.on_reload(self._kv_store_on_reload)
        self._logger.info("Start consuming on queue {0}..."
                          .format(self._kv_store.get(self._queue_name_key,
                                                     self._queue_name_default)))
        self._setup_publishers_and_consumers({}, {}, force=True)
        self._logger.info("Consuming messages on queue {0}."
                          .format(self._kv_store.get(self._queue_name_key,
                                                     self._queue_name_default)))

    def publish_success(self, data, properties=None):
        """
            Publishes a message to the success queue.

            :param data: The payload.
            :param properties: The properties for the payload.
        """
        self._done_producer.publish(data, properties)

    def publish_error(self, data, properties=None):
        """
            Publishes a message to the error queue.

            :param data: The payload.
            :param properties: The properties for the payload.
        """
        self._error_producer.publish(data, properties)

    def _callback_wrapper(self, ch, method, properties, body):
        """
        Calls the callback method, handles Exceptions, publishes error details to the error queue, an acknowledges
        errors.
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        self._logger.debug("Calling callback...")
        try:
            self._callback(ch, method, properties, body)
        except Exception as exception:
            error_message = "Error while processing message on the `{0}` exchange with a `{1}` binding key." \
                .format(method.exchange, method.routing_key)

            self._logger.error(error_message)
            stacktrace = traceback.format_exc()
            self._logger.error(exception)
            self._logger.error(stacktrace)

            try:
                message = json.loads(body.decode("utf-8"))
            except:
                message = body.decode("utf-8")

            error_body = {
                self._error_original_payload_key: message,
                'message': stacktrace.splitlines()[-1] if stacktrace else error_message,
                'error_details': stacktrace,
                'errorDetails': stacktrace
            }
            self.publish_error(json.dumps(error_body), properties)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        self._logger.debug("Done calling callback")

    def _kv_store_on_reload(self, old_config, new_config):
        self._setup_publishers_and_consumers(old_config, new_config)

    def _setup_publishers_and_consumers(self, old_config, new_config, force=False):

        if force or self._kv_store.attribute_changed_in_dict(old_config, new_config,
                                                             self._rabbit_host_key,
                                                             self._rabbit_port_key,
                                                             self._rabbit_user_key,
                                                             self._rabbit_password_key,
                                                             self._done_exchange_key,
                                                             self._done_routing_key_key,
                                                             self._error_exchange_key,
                                                             self._error_routing_key_key,
                                                             self._queue_name_key,
                                                             self._listen_exchange_key,
                                                             self._listen_routing_key_key,
                                                             self._amqp_connection_key):
            self._logger.info("Initializing RabbitMQ pubilishers and consumers...")
            # Setup done producer
            self._done_producer = self._new_queue_producer(self._kv_store.get(self._rabbit_host_key,
                                                                              self._rabbit_host_default),
                                                           self._kv_store.get(self._rabbit_port_key,
                                                                              self._rabbit_port_default),
                                                           self._kv_store.get(self._rabbit_user_key,
                                                                              self._rabbit_user_default),
                                                           self._kv_store.get(self._rabbit_password_key,
                                                                              self._rabbit_password_default),
                                                           self._kv_store.get(self._done_exchange_key,
                                                                              self._done_exchange_default),
                                                           self._kv_store.get(self._done_routing_key_key,
                                                                              self._done_routing_key_default))

            # Setup error producer
            self._error_producer = self._new_queue_producer(self._kv_store.get(self._rabbit_host_key,
                                                                               self._rabbit_host_default),
                                                            self._kv_store.get(self._rabbit_port_key,
                                                                               self._rabbit_port_default),
                                                            self._kv_store.get(self._rabbit_user_key,
                                                                               self._rabbit_user_default),
                                                            self._kv_store.get(self._rabbit_password_key,
                                                                               self._rabbit_password_default),
                                                            self._kv_store.get(self._error_exchange_key,
                                                                               self._error_exchange_default),
                                                            self._kv_store.get(self._error_routing_key_key,
                                                                               self._error_routing_key_default))
            # Setup queue consumers
            if self._queue_factory:
                self._queue_factory.stop_consuming()

            self._queue_factory = self._new_queue_factory(self._kv_store.get(self._rabbit_host_key,
                                                                             self._rabbit_host_default),
                                                          self._kv_store.get(self._rabbit_port_key,
                                                                             self._rabbit_port_default),
                                                          self._kv_store.get(self._rabbit_user_key,
                                                                             self._rabbit_user_default),
                                                          self._kv_store.get(self._rabbit_password_key,
                                                                             self._rabbit_password_default),
                                                          self._kv_store.get(self._listen_exchange_key,
                                                                             self._listen_exchange_default),
                                                          self._kv_store.get(self._queue_name_key,
                                                                             self._queue_name_default),
                                                          self._kv_store.get(self._listen_routing_key_key,
                                                                             self._listen_routing_default),
                                                          self._kv_store.get(self._amqp_connection_key,
                                                                             self._amqp_connection_default),
                                                          self._callback)
            self._logger.info("Done Initializing RabbitMQ pubilishers and consumers.")

    def _new_queue_factory(self,
                           rabbit_host,
                           rabbit_port,
                           rabbit_user,
                           rabbit_password,
                           exchange,
                           queue_name,
                           binding_key,
                           amqp_connections,
                           callback):
        self._logger.debug("Creating queue factory with the following parameters:")
        self._logger.debug("rabbit_host={0}".format(str(rabbit_host)))
        self._logger.debug("rabbit_port={0}".format(str(rabbit_port)))
        self._logger.debug("rabbit_user={0}".format(str(rabbit_user)))
        self._logger.debug("rabbit_password={0}".format(str(rabbit_password)))
        self._logger.debug("exchange={0}".format(str(exchange)))
        self._logger.debug("queue_name={0}".format(str(queue_name)))
        self._logger.debug("binding_key={0}".format(str(binding_key)))
        self._logger.debug("amqp_connections={0}".format(str(amqp_connections)))
        self._logger.debug("callback={0}".format(str(callback)))
        amqp_connections = int(amqp_connections)
        queue_factory_config = {
            "queue_config": []
        }

        x = 0
        while x < amqp_connections:
            queue_config = {
                "name": "{0}_{1}".format(queue_name, str(x)),
                "type": "consumer",
                "queue": queue_name,
                "host": rabbit_host,
                "port": rabbit_port,
                "binding_key": binding_key,
                "exchange": {
                    "name": exchange,
                    "type": "x-delayed-message",
                    "arguments": {"x-delayed-type": "topic"},
                    "durable": True
                },
                "auth": {
                    "user": rabbit_user,
                    "password": rabbit_password
                }
            }
            queue_factory_config["queue_config"].append(queue_config)
            x = x + 1

        self._logger.info("Creating {0} worker threads for queue {1}..."
                          .format(str(len(queue_factory_config["queue_config"])),
                                  queue_name))
        self._logger.debug("queue_factory_config:" + str(queue_factory_config))
        queue_factory = QueueFactory()
        queue_factory.create_consumers(queue_factory_config)
        self._logger.info("Start consuming {0} worker threads for queue {1}..."
                          .format(str(len(queue_factory_config["queue_config"])),
                                  queue_name))
        queue_factory.start_consuming(self._callback_wrapper)
        self._logger.info("{0} worker threads waiting to consume messages on queue {1}..."
                          .format(str(len(queue_factory_config["queue_config"])),
                                  queue_name))
        return queue_factory

    def _new_queue_producer(self,
                            rabbit_host,
                            rabbit_port,
                            rabbit_user,
                            rabbit_password,
                            exchange,
                            binding_key):
        self._logger.debug("Creating queue producer with the following parameters:")
        self._logger.debug("rabbit_host={0}".format(str(rabbit_host)))
        self._logger.debug("rabbit_port={0}".format(str(rabbit_port)))
        self._logger.debug("rabbit_user={0}".format(str(rabbit_user)))
        self._logger.debug("rabbit_password={0}".format(str(rabbit_password)))
        self._logger.debug("exchange={0}".format(str(exchange)))
        self._logger.debug("binding_key={0}".format(str(binding_key)))

        queue_config = {
            "type": "producer",
            "host": rabbit_host,
            "port": rabbit_port,
            "binding_key": binding_key,
            "exchange": {
                "name": exchange,
            },
            "auth": {
                "user": rabbit_user,
                "password": rabbit_password
            }
        }

        return QueueProducer(queue_config)
