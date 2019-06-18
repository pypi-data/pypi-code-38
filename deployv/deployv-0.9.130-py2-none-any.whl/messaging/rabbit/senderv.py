# coding: utf-8
import logging
import pika
import simplejson as json
from deployv.messaging import basemsg
from deployv.messaging.rabbit.rabbitv import BaseRabbitConfiguration

_logger = logging.getLogger(__name__)


class RabbitSenderV(object):
    """ A simple rabbit mq interface just pass the config parameters
    and send the message

    """
    def __init__(self, sender_configuration, sender_id):
        assert isinstance(sender_configuration, BaseRabbitConfiguration)
        self.__config = sender_configuration.get_result_object()
        self.__id = sender_id
        self.__connection = None
        self.__channel = None

    def connect(self):
        self.__connection = pika.BlockingConnection(self.__config.parameters)
        self.open_channel()

    def open_channel(self):
        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(queue=self.__config.queue_name, durable=True)
        self.__channel.exchange_declare(exchange=self.__config.exchange_name,
                                        type='topic')

    def reconnect(self):
        """ Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        if self.__connection:
            self.__connection.ioloop.stop()

        # if not self._closing:

            # Create a new connection
        self.connect()

    def amq_send_message(self, message, send_to=None):
        """ Send a message to the queue using the specified route

        :param message: Message to be delivered
        :param send_to: message route if none is provided will use default
                        passed to the class constructor
        :return: Pika basic_publish return value
        """
        self.connect()
        if send_to is not None and not self.__config.result_config:
            routing_key = '{route}.{worker}'.format(route=self.__config.route, worker=send_to)
        else:
            routing_key = self.__config.route
        _logger.debug('Sending message (%s): %s', routing_key, message)
        retry = 0
        while retry <= 3:
            try:
                if self.__connection.is_open:
                    res = self.__channel.basic_publish(self.__config.exchange_name,
                                                       routing_key=routing_key,
                                                       body=message,
                                                       properties=self.__config.properties,
                                                       )
                    retry = 4
                else:
                    self.__connection.add_timeout(self.__config.parameters.socket_timeout,
                                                  self.reconnect)
            except pika.exceptions.ConnectionClosed:
                retry += 1
                _logger.info('Connection failed, retry %s', retry)
                if retry == 3:
                    raise
                else:
                    self.reconnect()
                    # self.__connection.add_timeout(self.__config.parameters.socket_timeout,
                    #                               self.reconnect)
        self.__connection.close()
        return res

    def send_message(self, message, send_to=None):
        """ Sends a message via rabbit to the specified topic but first checks if the message
        is a MessageV instance

        :param message: MessageV instance
        :param send_to: Node or topic where the message will be sent
        :return: Response from the sender and the original message as string
        """
        assert isinstance(message, (basemsg.BasicMessage, dict))

        if isinstance(message, basemsg.BasicMessage):
            message_str = message.get_message_str()
        else:
            message_str = json.dumps(message,
                                     ensure_ascii=True,
                                     check_circular=True,
                                     encoding='utf-8')
        res = self.amq_send_message(message_str, send_to)
        return res, message_str

    def __del__(self):
        if self.__connection:
            self.__connection.close()
