# -*- coding: utf-8 -*-

import os
import pprint

from source.mail.receiver import Receiver, ReceiverException

CONFIG = '../../source/config/config.json'


def test_receiver():
    data = None
    try:
        receiver = Receiver(os.path.join(os.path.dirname(__file__), CONFIG))
        receiver.connect()
        pprint.pprint('count: %s. size: %s' % receiver.stat())
        data = receiver.retrieve()
        receiver.disconnect()
    except ReceiverException as err:
        pprint.pprint(str(err))
    assert (data is not None)
    pprint.pprint(data)
