# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

import json
from logging import getLogger

from odcs.server import conf

log = getLogger(__name__)

__all__ = ('publish',)


def publish(msgs):
    """Start to send messages to message broker"""
    backend = _get_messaging_backend()
    if backend is not None:
        backend(msgs)


def _umb_send_msg(msgs):
    """Send message to Unified Message Bus"""

    import proton
    from rhmsg.activemq.producer import AMQProducer

    config = {
        'urls': conf.messaging_broker_urls,
        'certificate': conf.messaging_cert_file,
        'private_key': conf.messaging_key_file,
        'trusted_certificates': conf.messaging_ca_cert,
    }
    with AMQProducer(**config) as producer:
        producer.through_topic(conf.messaging_topic)

        for msg in msgs:
            outgoing_msg = proton.Message()
            outgoing_msg.body = json.dumps(msg)
            producer.send(outgoing_msg)


def _fedmsg_send_msg(msgs):
    """Send message to fedmsg!  Yay!"""

    import fedmsg

    for msg in msgs:
        # "event" is typically just "state-changed"
        event = msg.get('event', 'event')
        topic = "compose.%s" % event
        fedmsg.publish(topic=topic, msg=msg)


def _get_messaging_backend():
    if conf.messaging_backend == 'rhmsg':
        return _umb_send_msg
    elif conf.messaging_backend == 'fedmsg':
        return _fedmsg_send_msg
    elif conf.messaging_backend:
        raise ValueError(
            'Unknown messaging backend {0}'.format(conf.messaging_backend))
    else:
        return None
