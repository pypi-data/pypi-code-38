# encoding: utf-8
import unittest

from hyperstools.mq.lib import Queue

RABBITMQ = {
    "host": "saas-mqi.hypers.cc",
    "port": 5672,
    "vhost": "/aurora",
    "user": "aurora",
    "password": "hypersadmin",
    "heart_beat": 0,
    "queue": "test",
}


@Queue(RABBITMQ)
def listen(body):
    print(body)


class TestMq(unittest.TestCase):
    def test_publish(self):
        Queue(RABBITMQ).publish({})

    def test_publish_pickle(self):
        Queue(RABBITMQ).publish({}, encoder="pickle")

    def test_listen(self):
        pass
        #listen()
