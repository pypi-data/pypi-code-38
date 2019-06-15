# -*- coding: utf-8 -*-

import logging
import os

from mailtrigger.mailer.receiver import Receiver, ReceiverException

CONFIG = '../../mailtrigger/config/mailer.json'


def test_receiver():
    log = logging.getLogger('test_scheduler')
    data = None

    try:
        receiver = Receiver(os.path.join(os.path.dirname(__file__), CONFIG))
        receiver.connect()
        log.debug('count: %s. size: %s' % receiver.stat())
        _ = receiver.retrieve()
        receiver.disconnect()
    except ReceiverException as err:
        log.error(str(err))

    assert (data is not None)
