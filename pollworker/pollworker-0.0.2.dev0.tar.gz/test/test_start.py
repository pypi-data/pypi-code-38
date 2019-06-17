# coding=utf8
from unittest import TestCase
import time

__author__ = 'Alexander.Li'


class TestStart(TestCase):
    def test_start(self):
        import pollworker

        def worker(pid, message):
            print("worker({0}) recv:{1}".format(pid, message))

        class Poller(object):
            def poll(self):
                time.sleep(2)
                return str(time.time())

        pollworker.regist_worker(worker)
        pollworker.regist_poller(Poller())
        pollworker.start(stopwaits=3)

        self.assertTrue(True)
