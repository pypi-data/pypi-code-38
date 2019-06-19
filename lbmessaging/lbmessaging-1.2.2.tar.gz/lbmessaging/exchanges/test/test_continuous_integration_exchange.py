import logging
import sys
import unittest

from lbmessaging.exchanges.test import get_test_connection

from lbmessaging.exchanges.ContinuousIntegrationExchange import \
    ContinuousIntegrationExchange

QUEUE_NAME = "test_build_ready_queue"
QUEUE_NAME_ENV_KIT = "test_env_kit_ready_queue"


class TestContinuousIntegrationExchange(unittest.TestCase):

    def setUp(self):
        self._connection = get_test_connection()
        self._channel = self._connection.channel()

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def test_build_ready_simple(self):
        """ Check whether a simple command gets through """
        slot = "slot1"
        build_id = "1"
        platform = "x86_64-centos7-gcc62-opt"
        project = "project1"
        broker = ContinuousIntegrationExchange(self._channel)
        broker.receive_all_build_ready(QUEUE_NAME)
        broker.send_build_ready(slot, build_id, platform, project)
        tmp = broker.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project, tmp.body.project)

    def test_env_kit_ready_simple(self):
        """ Check whether a simple command gets through """
        flavour = 'dev'
        platform = "centos7"
        version = '243535.2018-01-01'
        broker = ContinuousIntegrationExchange(self._channel)
        broker.receive_all_envkit_ready(QUEUE_NAME_ENV_KIT)
        broker.send_envkit_ready(flavour, platform, version)
        tmp = broker.receive_envkit_ready(QUEUE_NAME_ENV_KIT)
        self.assertEqual(flavour, tmp.body.flavour)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(version, tmp.body.version)
        self.assertEqual(None, tmp.body.url)

    def test_first_come_first_served_build_ready(self):
        """ Check the priority system """

        broker = ContinuousIntegrationExchange(self._channel)

        # purge the queue
        broker.receive_all_build_ready(QUEUE_NAME)

        # Now adding our slots
        slot = "slot1"
        build_id = "1"
        platform = "x86_64-centos7-gcc62-opt"
        project1 = "project1"
        project2 = "project2"
        project3 = "project3"
        broker.send_build_ready(slot, build_id, platform, project1)
        broker.send_build_ready(slot, build_id, platform, project2)
        broker.send_build_ready(slot, build_id, platform, project3)

        # Make sure we get the first come first served
        tmp = broker.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project1, tmp.body.project)

        tmp = broker.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project2, tmp.body.project)

        tmp = broker.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project3, tmp.body.project)

    def test_first_come_first_served_env_kit_ready(self):
        """ Check the priority system """

        broker = ContinuousIntegrationExchange(self._channel)

        # purge the queue
        broker.receive_all_envkit_ready(QUEUE_NAME_ENV_KIT)

        # Now adding our slots
        flavour = 'dev'
        platform = "centos7"
        version1 = '243535.2018-01-01'
        version3 = "243536.2018-01-01"
        version2 = "243537.2018-01-01"

        broker.send_envkit_ready(flavour, platform, version1)
        broker.send_envkit_ready(flavour, platform, version2)
        broker.send_envkit_ready(flavour, platform, version3)

        # Make sure we get the first come first served
        tmp = broker.receive_envkit_ready(QUEUE_NAME_ENV_KIT)
        self.assertEqual(flavour, tmp.body.flavour)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(version1, tmp.body.version)

        tmp = broker.receive_envkit_ready(QUEUE_NAME_ENV_KIT)
        self.assertEqual(flavour, tmp.body.flavour)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(version2, tmp.body.version)

        tmp = broker.receive_envkit_ready(QUEUE_NAME_ENV_KIT)
        self.assertEqual(flavour, tmp.body.flavour)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(version3, tmp.body.version)

    def test_consumer_build_ready(self):
        """ Check whether a simple command gets through """
        slot = "slot1"
        build_id = "1"
        platform = "x86_64-centos7-gcc62-opt"
        project = "project1"
        broker = ContinuousIntegrationExchange(self._channel)
        broker.receive_all_build_ready(QUEUE_NAME)
        broker.send_build_ready(slot, build_id, platform, project)
        broker.send_build_ready("EXIT", build_id, platform, project)

        def checkbuildisok(tmp):
            if tmp.body.slot == "EXIT":
                raise StopIteration
            else:
                self.assertEqual(slot, tmp.body.slot)
                self.assertEqual(build_id, tmp.body.build_id)
                self.assertEqual(platform, tmp.body.platform)
                self.assertEqual(project, tmp.body.project)
        broker.consume_build_ready(checkbuildisok, QUEUE_NAME)

    def test_consumer_env_kit_ready(self):
        """ Check whether a simple command gets through """
        flavour = 'dev'
        platform = "centos7"
        version = '243535.2018-01-01'
        broker = ContinuousIntegrationExchange(self._channel)
        broker.receive_all_envkit_ready(QUEUE_NAME_ENV_KIT)
        broker.send_envkit_ready(flavour, platform, version)
        broker.send_envkit_ready('EXIT', platform, version)

        def checkbuildisok(tmp):
            if tmp.body.flavour == "EXIT":
                raise StopIteration
            else:
                self.assertEqual(flavour, tmp.body.flavour)
                self.assertEqual(platform, tmp.body.platform)
                self.assertEqual(version, tmp.body.version)
        broker.consume_envkit_ready(checkbuildisok, QUEUE_NAME_ENV_KIT)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
