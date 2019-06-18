import odoo_manager
from subprocess import PIPE, Popen as popen
from unittest import TestCase


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(["odoo-manager", "-h"], stdout=PIPE).communicate()[0]
        self.assertTrue("Usage:" in output)

        output = popen(["odoo-manager", "--help"], stdout=PIPE).communicate()[0]
        self.assertTrue("Usage:" in output)


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(["odoo-manager", "--version"], stdout=PIPE).communicate()[0]
        self.assertEqual(output.strip(), odoo_manager.version)
