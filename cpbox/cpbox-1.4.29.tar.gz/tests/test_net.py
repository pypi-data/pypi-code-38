import unittest
from cpbox.tool import net
from cpbox.tool import dockerutil
from cpbox.tool import system

class TestNet(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all(self):
        if system.get_os_name() == 'mac':
            self.assertRaises(IOError, net.get_ip_address, 'docker0')
        else:
            ip1 = net.get_ip_address('docker0')
            ip2 = dockerutil.get_docker_network_gw('bridge')
            self.assertEqual(ip1, ip2)

if __name__ =='__main__':
    unittest.main()