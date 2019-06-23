# -*- coding: utf-8 -*-

import json
import os
import sys
import time

from .argument import Argument
from .banner import BANNER
from .logger.logger import Logger
from .mailer.receiver import Receiver, ReceiverException
from .mailer.sender import Sender, SenderException
from .registry import Registry, RegistryException
from .scheduler.scheduler import Scheduler, SchedulerException
from .trigger.trigger import TriggerException


def _send(data, msg, sender):
    def _format(data, msg):
        return {
            'content': os.linesep.join((
                msg,
                '%s' % ('-'*80),
                '> From: %s' % data['from'],
                '> To: %s' % data['to'],
                '> Subject: %s' % data['subject'],
                '> Date: %s' % data['date'],
                '> Content: %s' % data['content'])),
            'date': time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())),
            'from': data['to'],
            'subject': 'Re: %s' % data['subject'],
            'to': [data['from'], data['to']]
        }

    sender.connect()
    sender.send(_format(data, msg))
    sender.disconnect()


def _trigger(data, sender, trigger):
    for item in trigger:
        msg, status = item.run(data)
        if status is True:
            _send(data, msg, sender)


def _receive(receiver):
    receiver.connect()
    data = receiver.receive(1)
    receiver.disconnect()
    return data


def _job(args):
    receiver, sender, trigger = args
    _trigger(_receive(receiver), sender, trigger)


def _scheduler(sched, receiver, sender, trigger):
    sched.add(_job, [receiver, sender, trigger], '_job')
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
    args = argument.parse(sys.argv)

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
    except ReceiverException as e:
        Logger.error(str(e))
        sched.stop()
        return -5

    try:
        sender = Sender(mailer_config)
    except SenderException as e:
        Logger.error(str(e))
        sched.stop()
        return -6

    try:
        registry = Registry(trigger_config)
        trigger = registry.instantiate()
    except (RegistryException, TriggerException) as e:
        Logger.error(str(e))
        sched.stop()
        return -7

    ret = 0

    try:
        _scheduler(sched, receiver, sender, trigger)
    except (SchedulerException, ReceiverException, SenderException, TriggerException) as e:
        Logger.error(str(e))
        ret = -8
    finally:
        sender.disconnect()
        receiver.disconnect()
        sched.stop()

    return ret
