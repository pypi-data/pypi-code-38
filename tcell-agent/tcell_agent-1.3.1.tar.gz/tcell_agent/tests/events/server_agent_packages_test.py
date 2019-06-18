import unittest

from tcell_agent.events.server_agent_packages import ServerAgentPackagesEvent


class SanitizerUtilsTest(unittest.TestCase):
    def test_package_event_create(self):
        sape = ServerAgentPackagesEvent()
        sape.add_package("test_package", "test_version")
        self.assertEqual(sape["packages"], [{"n": "test_package", "v": "test_version"}])

    def test_packages_event_create(self):
        sape = ServerAgentPackagesEvent()
        sape.add_package("test_package", "test_version")
        sape.add_package("test_package2", "test_version2")
        self.assertEqual(sape["packages"], [
            {"n": "test_package", "v": "test_version"},
            {"n": "test_package2", "v": "test_version2"}
        ])
