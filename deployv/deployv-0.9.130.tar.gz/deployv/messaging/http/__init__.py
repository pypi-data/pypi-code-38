# coding: utf-8

from deployv.messaging.http.worker import HttpWorker
from deployv.messaging.http.httpv import FileHttpConfiguration, BaseHttpConfiguration
from deployv.messaging.http.receiverv import HttpReceiverV
from deployv.messaging.http.senderv import HttpSenderV


CONFIG_CLASSES = {
    'base': BaseHttpConfiguration,
    'file': FileHttpConfiguration
}


def factory(config_object, worker_id):
    http_worker = HttpWorker(config_object, HttpSenderV, HttpReceiverV, worker_id)
    return http_worker
