import os

from unittest import TestCase, mock

CF_DOCKER_IMAGE_PREFIX = 'test.registry.prefix.com'

os.environ['CF_DOCKER_IMAGE_PREFIX'] = CF_DOCKER_IMAGE_PREFIX


class BaseTestCase(TestCase):
    def setUp(self):
        # disconnect any remote docker hosts
        os.environ.pop('DOCKER_HOST', None)

        super().setUp()

        self.sh_patcher = mock.patch('compose_flow.shell.sh')
        self.sh_mock = self.sh_patcher.start()

    def tearDown(self):
        self.sh_patcher.stop()
