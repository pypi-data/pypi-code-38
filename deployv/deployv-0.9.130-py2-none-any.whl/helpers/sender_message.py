# coding: utf-8

import logging
from deployv.messaging.basemsg import BasicMessage
from deployv.messaging.rabbit import rabbitv, senderv
from pika.exceptions import ConnectionClosed
from datetime import datetime

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SenderMessage(object):

    def __init__(self, config):
        self.__config = config
        rabbit_obj = rabbitv.FileRabbitConfiguration(self.__config, result=True)
        self._rabbit_sender = senderv.RabbitSenderV(
            rabbit_obj, self.__config.deployer.get('node_id'))

    def send_message(self, msg=False, body=False, log_type='INFO'):
        """Method fo send a message via rabbit to the specified topic in
        anywhere of process.

        :param message: the message that will be sended.
        :type message: dict.
        """
        if not msg and not body:
            logger.error('Unable to send the message, you must specify a message to send')
            return
        message = BasicMessage()
        message.sender_node_id = self.__config.sender_node_id or (
            self.__config.deployer.get('node_id'))
        message.receiver_node_id = self.__config.receiver_node_id or (
            self.__config.deployer.get('orchest_receiver_id'))
        message.user_id = self.__config.user_id
        message.res_id = self.__config.res_id
        message.deploy_id = self.__config.deploy_id
        message.res_model = self.__config.res_model
        message.model = self.__config.model
        message_body = {
            'module': 'commandv',
            'command': 'save_msg_process',
            'task_id': self.__config.instance_config.get('task_id'),
            'customer_id': self.__config.instance_config.get('customer_id')
        }
        if body:
            message_body.update(body)
        if msg:
            log = logger.info if log_type == 'INFO' else logger.error
            log(msg)
            message_body.update({'log': '{time} {type} {module}: {msg}'.format(
                time=datetime.utcnow().isoformat(' '), type=log_type, module=self.__config.command,
                msg=msg)
            })
        message.set_message_body(message_body, message_type='result')
        if not message.receiver_node_id:
            logger.warning('Failed to send the message: The receiver is required')
            return
        try:
            self._rabbit_sender.send_message(message)
        except ConnectionClosed:
            logger.warning('Failed to send the message: Lost connection with rabbit')
