# -*- coding: utf-8 -*-

import json
import logging
import os
import time

from mailtrigger.mailer.sender import Sender, SenderException

CONFIG = '../../mailtrigger/config/mailer.json'
TEST = '../test_data.json'


def test_sender():
    log = logging.getLogger('test_sender')
    status = True

    with open(os.path.join(os.path.dirname(__file__), TEST), 'r') as f:
        data = json.load(f)

    buf = {
        'content': '\n'.join((
            'pytest',
            '%s' % ('-'*80),
            '> From: %s' % data['from'],
            '> To: %s' % data['to'],
            '> Subject: %s' % data['subject'],
            '> Date: %s' % data['date'],
            '> Content: %s' % data['content'])),
        'date': time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())),
        'from': data['to'],
        'subject': 'Re: %s' % data['subject'],
        'to': data['from']
    }

    try:
        sender = Sender(os.path.join(os.path.dirname(__file__), CONFIG))
        sender.connect()
        sender.send(buf)
        sender.disconnect()
    except SenderException as err:
        log.error(str(err))
        status = False

    assert (status is True)
