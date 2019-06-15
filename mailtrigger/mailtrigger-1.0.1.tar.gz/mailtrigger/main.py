# -*- coding: utf-8 -*-

import os
import time

from .argument import Argument
from .banner import BANNER
from .logger.logger import Logger
from .mailer.receiver import Receiver, ReceiverException
from .mailer.sender import Sender, SenderException
from .registry import REGISTRY
from .scheduler.scheduler import Scheduler, SchedulerException
from .trigger.trigger import TriggerException

MAILER = 'config/mailer.json'
SCHEDULER = 'config/scheduler.json'

HELP = 'help'
TRIGGER = '[trigger]'


def _format(data, content):
    return {
        'content': '\n'.join((
            content,
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


def _emit(data, sender, triggers):
    """TODO"""


def _help(data, sender, triggers):
    buf = []
    for item in triggers:
        buf.append('@%s %s' % (item, HELP))
    sender.connect()
    sender.send(_format(data, os.linesep.join(buf)))
    sender.disconnect()


def _trigger(data, sender, triggers):
    for item in data:
        t = item['content'].split()[0].lstrip('@').strip()
        if t == HELP:
            _help(item, sender, triggers)
        else:
            _emit(item, sender, triggers)


def _unpack(data):
    def _unpack_helper(data):
        buf = []
        lines = data['content'].splitlines()
        for item in lines:
            if len(item.strip()) != 0:
                data['content'] = item.strip()
                buf.append(data)
        return buf

    buf = []
    for item in data:
        buf.extend(_unpack_helper(item))

    return buf


def _filter(data):
    def _filter_helper(data):
        ret = False
        if data['subject'].startswith(TRIGGER):
            ret = True
        return ret

    buf = []
    for item in data:
        if _filter_helper(item) is True:
            buf.append(item)

    return buf


def _retrieve(receiver):
    receiver.connect()
    data = receiver.retrieve()
    receiver.disconnect()
    return data


def _job(args):
    receiver, sender, triggers = args
    data = _retrieve(receiver)
    data = _filter(data)
    data = _unpack(data)
    _trigger(data, sender, triggers)


def _scheduler(sched, receiver, sender, triggers):
    sched.add(_job, [receiver, sender, triggers], '_job')

    while True:
        sched.run()
        time.sleep(1)


def main():
    print(BANNER)

    argument = Argument()
    args = argument.parse()

    triggers = args.trigger.split(',')
    buf = list(set(triggers) - set([r['name'] for r in REGISTRY]))
    if len(buf) != 0:
        Logger.error('invalid trigger %s' % ','.join(buf))
        return -1

    try:
        sched = Scheduler(os.path.join(os.path.dirname(__file__), SCHEDULER))
    except SchedulerException as e:
        Logger.error(str(e))
        return -2

    try:
        receiver = Receiver(os.path.join(os.path.dirname(__file__), MAILER))
        sender = Sender(os.path.join(os.path.dirname(__file__), MAILER))
    except (ReceiverException, SenderException) as e:
        Logger.error(str(e))
        sched.stop()
        return -3

    ret = 0

    try:
        _scheduler(sched, receiver, sender, triggers)
    except (SchedulerException, ReceiverException, SenderException, TriggerException) as e:
        Logger.error(str(e))
        ret = -4
    finally:
        sender.disconnect()
        receiver.disconnect()
        sched.stop()

    return ret
