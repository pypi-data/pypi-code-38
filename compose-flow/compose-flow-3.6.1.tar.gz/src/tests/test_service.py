import re
import shlex

from unittest import mock

from compose_flow.commands import Workflow

from tests import BaseTestCase


class ServiceTestCase(BaseTestCase):
    def test_runs(self, *mocks):
        """
        Basic test to ensure the command runs as expected
        """
        argv = shlex.split('-e test service exec app /bin/bash')
        workflow = Workflow(argv=argv)

        service = workflow.subcommand

        service.select_container = mock.MagicMock()
        service.select_container.return_value = (
            'container_id service_name something test_hostname'
        )

        workflow.run()

        ssh_mock = self.sh_mock.ssh
        ssh_args = ssh_mock.mock_calls[0][1]

        args_s = ' '.join(ssh_args)

        command_re = re.compile(r'docker exec .* service_name\.container_id /bin/bash')

        self.assertEqual(True, command_re.search(args_s) is not None)
