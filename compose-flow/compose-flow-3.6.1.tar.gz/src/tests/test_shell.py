from unittest import TestCase, mock

from compose_flow import shell

from tests import BaseTestCase


class ShellTestCase(BaseTestCase):
    @mock.patch('compose_flow.shell.OS_ENV_INCLUDES', new_callable=dict)
    def test_execute(self, *mocks):
        """
        Ensure the shell's execution is done with the passed in environment
        """
        env = {}

        shell.execute('docker ps', env)

        self.sh_mock.docker.assert_called_with('ps', _env=env)
