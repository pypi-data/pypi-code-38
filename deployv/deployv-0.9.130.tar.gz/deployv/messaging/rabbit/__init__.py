# coding: utf-8

from .worker import RabbitWorker
from .rabbitv import FileRabbitConfiguration, BaseRabbitConfiguration
from .receiverv import RabbitReceiverV
from .senderv import RabbitSenderV


CONFIG_CLASSES = {
    'base': BaseRabbitConfiguration,
    'file': FileRabbitConfiguration
}


def factory(config_object, worker_id):
    rabbit_worker = RabbitWorker(config_object,
                                 RabbitSenderV,
                                 RabbitReceiverV,
                                 worker_id
                                 )
    return rabbit_worker
