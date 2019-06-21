from unittest import TestCase, mock
import re

from compose_flow.environment.backends import get_backend


@mock.patch('compose_flow.environment.backends.local_backend.open')
@mock.patch('compose_flow.environment.backends.local_backend.os')
class LocalBackendTestCase(TestCase):
    buf = 'FOO=1\n'

    @property
    def backend(self):
        backend = get_backend('local')

        return backend

    def _setup_mocks(self, *mocks):
        open_mock = mocks[-1]
        open_mock.return_value.__enter__.return_value.read.return_value = self.buf

        os_mock = mocks[-2]
        os_mock.listdir.return_value = ['foo']

    def test_list(self, *mocks):
        self._setup_mocks(*mocks)

        self.assertEqual(self.backend.ls(), ['foo'])

    def test_read(self, *mocks):
        self._setup_mocks(*mocks)

        self.assertEqual(self.backend.read('foo'), self.buf)

    def test_write(self, *mocks):
        self._setup_mocks(*mocks)

        self.backend.write('foo', '/path/to/config')

        open_mock = mocks[-1]

        open_mock.return_value.__enter__.return_value.write.assert_called_with(self.buf)


@mock.patch('compose_flow.environment.backends.swarm_backend.docker')
class SwarmBackendTestCase(TestCase):
    buf = 'FOO=1\n'

    @property
    def backend(self):
        backend = get_backend('swarm')

        return backend

    def _setup_mocks(self, *mocks):
        self.docker_mock = mocks[-1]

    def test_list(self, *mocks):
        self._setup_mocks(*mocks)

        self.backend.ls()

        self.docker_mock.get_configs.assert_called()

    def test_read(self, *mocks):
        self._setup_mocks(*mocks)

        name = 'foo'

        self.backend.read(name)

        self.docker_mock.get_config.assert_called_with(name)

    def test_write(self, *mocks):
        self._setup_mocks(*mocks)

        name = 'foo'
        path = '/path/to/config'

        self.backend.write(name, path)

        self.docker_mock.load_config.assert_called_with(name, path)


class RancherBackend(TestCase):

    @property
    def backend(self):
        backend = get_backend('rancher')

        return backend

    @mock.patch('compose_flow.environment.backends.rancher_backend.RancherBackend.switch_rancher_context')
    @mock.patch('compose_flow.environment.backends.rancher_backend.RancherBackend._check_rancher_namespace')
    def test_secret_contains_no_invalid_characters(self, *mocks):
        """
        Test that when we store a secret all invalid characters are replaced with `-`
        """
        backend = self.backend
        backend.workflow = mock.MagicMock(config_name='dev-oss_reporting')

        validation_regex = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$')

        self.assertTrue(re.match(validation_regex, backend.secret_name) is not None)
