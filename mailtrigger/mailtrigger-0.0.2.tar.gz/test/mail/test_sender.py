# -*- coding: utf-8 -*-

import json
import os
import pprint
import time

from source.mail.sender import Sender, SenderException

CONFIG = '../../source/config/config.json'
TEST = '../test/mail.json'


def test_sender():
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
            '>',
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
        pprint.pprint(str(err))
        status = False
    assert (status is True)
