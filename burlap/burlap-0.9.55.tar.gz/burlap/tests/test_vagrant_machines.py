
from mock import patch

from burlap.tests.base import TestCase

class TestVagrantMachines(TestCase):

    def test_machines_one(self):
        with patch('burlap.vagrant.vagrant._status') as mock_status:
            mock_status.return_value = [('default', 'running')]
            from burlap.vagrant import vagrant
            self.assertEqual(vagrant.machines(), ['default'])
