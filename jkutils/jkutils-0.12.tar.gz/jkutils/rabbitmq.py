# -*- coding: utf-8 -*-

import logging
import traceback

import pika

LOGGER = logging.getLogger(__name__)


class MQPublisher:
    def __init__(self, amqp_url):
        self._url = amqp_url

    def publish(
        self,
        exchange: str,
        exchange_type: str,
        durable: bool,
        routing_key: str,
        msg: str,
        properties={},
        mandatory=False,
        immediate=False,
    ):
        """
        send msg
        :param exchange: exchange
        :param exchange_type: exchange_type
        :param durable: durable
        :param routing_key: routing_key
        :param msg: message
        :param properties: dict like {"delivery_mode":1} support https://pika.readthedocs.io/en/stable/modules/spec.html#pika.spec.BasicProperties
        :param mandatory: mandatory
        :param immediate: immediate
        :return:
        """
        try:

            parameters = pika.URLParameters(self._url)

            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable)
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=msg,
                properties=pika.BasicProperties(**properties),
                mandatory=mandatory,
                immediate=immediate,
            )
        except Exception as e:
            LOGGER.warning(f"send_msg:{str(e)}, Exception:{traceback.format_exc()}")
            raise
        finally:
            connection.close()
