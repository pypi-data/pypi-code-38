from mock import patch

from burlap.constants import *
from burlap.common import get_satchel, set_verbose, set_dryrun, OS
from burlap.tests.base import TestCase

class ServiceTests(TestCase):

    def test_post_deploy(self):
        with patch('burlap.common.get_os_version') as mock_get_os_version:
            mock_get_os_version.return_value = OS(
                type=LINUX,
                distro=UBUNTU,
                release='16.04')

            service = get_satchel('service')
            apache = get_satchel('apache')
            service.genv.services.append(apache.name)
            set_verbose(1)
            set_dryrun(1)
            print('self.genv.services:', service.genv.services)
            service.post_deploy()
