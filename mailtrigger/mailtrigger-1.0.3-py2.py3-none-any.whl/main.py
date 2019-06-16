# -*- coding: utf-8 -*-

import json
import os
import time

from .argument import Argument
from .banner import BANNER
from .logger.logger import Logger
from .mailer.receiver import Receiver, ReceiverException
from .mailer.sender import Sender, SenderException
from .registry import Registry
from .scheduler.scheduler import Scheduler, SchedulerException
from .trigger.trigger import TriggerException

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


def _emit(data, sender, registry):
    """TODO"""


def _help(data, sender, registry):
    buf = []
    for item in registry.list():
        buf.append('@%s %s' % (item, HELP))
    sender.connect()
    sender.send(_format(data, os.linesep.join(buf)))
    sender.disconnect()


def _trigger(data, sender, registry):
    for item in data:
        t = item['content'].split()[0].lstrip('@').strip()
        if t == HELP:
            _help(item, sender, registry)
        else:
            _emit(item, sender, registry)


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
    receiver, sender, registry = args
    data = _retrieve(receiver)
    data = _filter(data)
    data = _unpack(data)
    _trigger(data, sender, registry)


def _scheduler(sched, receiver, sender, registry):
    sched.add(_job, [receiver, sender, registry], '_job')

    while True:
        sched.run()
        time.sleep(1)


def _load(name):
    with open(name, 'r') as f:
        data = json.load(f)
    return data


def main():
    print(BANNER)

    argument = Argument()
    args = argument.parse()

    if args.debug is not None:
        debug = args.debug
    else:
        debug = False

    if os.path.exists(args.mailer_config) and args.mailer_config.endswith('.json'):
        mailer_config = _load(args.mailer_config)
        mailer_config['debug'] = debug
    else:
        Logger.error('invalid mailer configuration %s' % args.mailer_config)
        return -1

    if os.path.exists(args.scheduler_config) and args.scheduler_config.endswith('.json'):
        scheduler_config = _load(args.scheduler_config)
        scheduler_config['debug'] = debug
    else:
        Logger.error('invalid scheduler configuration %s' % args.scheduler_config)
        return -2

    if os.path.exists(args.trigger_config) and args.trigger_config.endswith('.json'):
        trigger_config = _load(args.trigger_config)
        trigger_config['debug'] = debug
    else:
        Logger.error('invalid trigger configuration %s' % args.trigger_config)
        return -3

    try:
        sched = Scheduler(scheduler_config)
    except SchedulerException as e:
        Logger.error(str(e))
        return -4

    try:
        receiver = Receiver(mailer_config)
        sender = Sender(mailer_config)
    except (ReceiverException, SenderException) as e:
        Logger.error(str(e))
        sched.stop()
        return -5

    registry = Registry()
    registry.fill(trigger_config)

    ret = 0

    try:
        _scheduler(sched, receiver, sender, registry)
    except (SchedulerException, ReceiverException, SenderException, TriggerException) as e:
        Logger.error(str(e))
        ret = -6
    finally:
        sender.disconnect()
        receiver.disconnect()
        sched.stop()

    return ret
