# coding=utf8

__author__ = 'Alexander.Li'

import multiprocessing
import logging
import json
import signal
import sys
from utilities import SingletonMixin, RedisConnection
from parser import FilebeatParser, Configure
from publisher import SNSPublisher, MailgunPublisher
from errorbuster import formatError


def signal_handler(signal, frame):
    sys.exit(0)


def worker_proccess(message,  config):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    configure = Configure.instance().restore(config)
    if configure.publisher == 'sns':
        logging.info('setup sns publisher')
        publisher = SNSPublisher.instance()
    else:
        logging.info('setup mailgun publisher')
        publisher = MailgunPublisher.instance()
    publisher.init_publisher(configure)
    try:
        filebeatparser = FilebeatParser(message)
        message = "\n".join([
            "HOST NAME: %s" % filebeatparser.host,
            "TIMESTAMP: %s" % filebeatparser.timestamp,
            "MESSAGE:\n%s" % json.dumps(filebeatparser.message, indent=4)
        ])
        publisher.sendMessage(message)
    except Exception as ex:
        logging.error(formatError(ex))


class Server(SingletonMixin):
    def start(self, configure, logging_level=logging.INFO):
        logging.basicConfig(
            level=logging_level,
            format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s'
        )
        RedisConnection.instance().initConnection(configure)
        try:
            queue = multiprocessing.Manager().Queue()
            pool = multiprocessing.Pool(processes=configure.workers)
            while True:
                qn, data = RedisConnection.instance().waitfor()
                if qn == configure.watch_key:
                    pool.apply_async(worker_proccess, args=(data, configure.config))
                    queue.put(data)

        except Exception as e:
            logging.error(formatError(e))
            pool.terminate()
            pool.join()

        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
