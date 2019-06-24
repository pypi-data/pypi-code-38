
# encoding: utf-8

import logging
from hyperstools.mq.lib import Queue
from hyperstools.mq import asyncTask
logging.basicConfig(filename='example.log',level=logging.DEBUG)


RABBITMQ = {
    "host": "saas-mqi.hypers.cc",
    "port": 5672,
    "vhost": "/aurora",
    "user": "aurora",
    "password": "hypersadmin",
    'queue': 'spider-captcha'
}
@asyncTask.register
def task():
    pass

task()
