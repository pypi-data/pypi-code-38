import logging
import sys
import unittest

from lbmessaging.services.LbCIService import LbCIService
from lbmessaging.exchanges.ContinuousIntegrationExchange \
    import ContinuousIntegrationExchange
from lbmessaging.exchanges.test import get_test_connection


QUEUE_NAME = "test_build_ready_queue"
QUEUE_NAME_ENV_KIT = "test_env_kit_ready_queue"


class TestLbCIService(unittest.TestCase):

    def setUp(self):
        channel = get_test_connection().channel()
        broker = ContinuousIntegrationExchange(channel)
        broker.receive_all_build_ready(QUEUE_NAME)
        broker.receive_all_envkit_ready(QUEUE_NAME_ENV_KIT)

    def tearDown(self):
        pass

    def test_compute_url(self):
        flavour = 'dev'
        platform = "centos7"
        version = '243535.2018-01-01'
        self.assertEqual(
            "http://lhcb-rpm.web.cern.ch/lhcb-rpm/lbenv-kits/"
            "lbenv-kit.dev.centos7.243535.2018-01-01.tar.bz2",
            LbCIService.getEnvKitUrl(flavour, platform, version)
        )
        self.assertEqual(
            "http://toto.cern.ch/here",
            LbCIService.getEnvKitUrl(flavour, platform, version,
                                     url='http://toto.cern.ch/here')
        )

    def test_getEnvKitPrefix(self):
        flavour = 'dev'
        platform = "centos7"
        self.assertEqual(
            "/cvmfs/lhcbdev.cern.ch/new-msr/var/lib/LbEnv/dev/centos7/",
            LbCIService.getEnvKitPrefix(flavour, platform)
        )
        try:
            flavour = '../../../toto'
            LbCIService.getEnvKitPrefix(flavour, platform)
            self.fail("A value error should have been raise")
        except ValueError:
            pass

    def test_services(self):
        srv = LbCIService(vhost='/lhcb-test')
        slot = "slot1"
        build_id = "1"
        platform = "x86_64-centos7-gcc62-opt"
        project = "project1"
        srv.send_build_ready(slot, build_id, platform, project)
        tmp = srv.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project, tmp.body.project)

    def test_service_tar_extract(self):
        srv = LbCIService(vhost='/lhcb-test')
        srv.send_envkit_ready('flavour', 'platform', 'version')
        tmp = srv.receive_envkit_ready(QUEUE_NAME_ENV_KIT)
        self.assertEqual('flavour', tmp.body.flavour)
        self.assertEqual('platform', tmp.body.platform)
        self.assertEqual('version', tmp.body.version)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
