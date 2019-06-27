import unittest
from cpbox.tool import dockerutil


class TestDockerUtil(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all(self):
        ip = dockerutil.get_docker_network_gw('bridge')


if __name__ == '__main__':
    unittest.main()
