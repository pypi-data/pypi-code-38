import uuid
import pika
from logging import Logger
from jsonpickle import json

from sidecar.utils import CallsLogger


class MessagingConnectionProperties:
    def __init__(self, host: str,
                 user: str,
                 password: str,
                 queue: str,
                 exchange: str,
                 routingkey: str,
                 virtualhost: str,
                 port: int,
                 queuetype: str,
                 expires: int,
                 usessl: bool):
        self.host = host
        self.user = user
        self.password = password
        self.queue = queue
        self.exchange = exchange
        self.routingkey = routingkey
        self.virtualhost = virtualhost
        self.port = port
        self.queuetype = queuetype
        self.expires = expires
        self.usessl = usessl

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.host == other.host and \
                   self.password == other.password and \
                   self.queue == other.queue and \
                   self.exchange == other.exchange and \
                   self.routingkey == other.routingkey and \
                   self.virtualhost == other.virtualhost and \
                   self.port == other.port and \
                   self.queuetype == other.queuetype and \
                   self.expires == other.expires and \
                   self.usessl == other.usessl
        return False

    def __repr__(self):
        return "host={} " \
               "queue={} " \
               "exchange={} " \
               "routingkey={} " \
               "virtualhost={} " \
               "port={} " \
               "queuetype={} " \
               "expires={} " \
               "usessl={}".format(self.host,
                                  self.password,
                                  self.queue,
                                  self.exchange,
                                  self.routingkey,
                                  self.virtualhost,
                                  self.port,
                                  self.queuetype,
                                  self.expires,
                                  self.usessl)


class MessagingService:
    def __init__(self, connection_props: MessagingConnectionProperties, logger: Logger):
        self._connection = None
        self._logger = logger

        scheme = "amqp" if connection_props.usessl is not True else "amqps"

        # virtual_host already starts with / to support no virtual host
        url = "{scheme}://{user}:{password}@{host}{virtual_host}?heartbeat_interval=0" \
            .format(scheme=scheme,
                    user=connection_props.user,
                    password=connection_props.password,
                    host=connection_props.host,
                    virtual_host=connection_props.virtualhost)
        self._url_params = pika.URLParameters(url=url)
        self._destination = "rabbitmq://{host}{virtual_host}/".format(host=connection_props.host,
                                                                      virtual_host=connection_props.virtualhost)
        self.endpoint = connection_props.queue

    @CallsLogger.wrap
    def publish(self, message_type: str, message):
        try:
            message_id = uuid.uuid1()
            payload = {
                "messageId": str(message_id),
                "conversationId": str(message_id),
                "destinationAddress": self._destination + message_type,
                "messageType": [
                    "urn:message:{}".format(message_type)
                ],
                "message": message,
                "headers": {}
            }

            connection = pika.BlockingConnection(self._url_params)
            # arguments = {"x-expires": self._connection_props.expires}
            # channel.queue_declare(queue=self._connection_props.queue, durable=True, arguments=arguments)
            channel = connection.channel()
            channel.basic_publish(exchange=self.endpoint, routing_key="", body=json.dumps(payload))
            connection.close()

        except Exception as exc:
            self._logger.exception("an error occurred while connecting to a queue {exc}".format(exc=exc))
