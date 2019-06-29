# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_fedora.upt_fedora import FedoraRubyPackage


class TestRubyGemsPackage(unittest.TestCase):
    def setUp(self):
        upt_pkg = upt.Package('foo', '42')
        self.fedora_pkg = FedoraRubyPackage(upt_pkg, None)

    def test_name(self):
        self.assertEqual(self.fedora_pkg.name, 'rubygem-%{gem_name}')

    def test_sourcename(self):
        self.assertEqual(self.fedora_pkg.sourcename, 'foo')

    def test_jinja2_reqformat(self):
        req = upt.PackageRequirement('foo', '>=1.0')
        out = self.fedora_pkg.jinja2_reqformat(req)
        expected = 'rubygem(foo) >=1.0'
        self.assertEqual(out, expected)

    def test_jinja2_reqformat_no_specifier(self):
        req = upt.PackageRequirement('foo')
        out = self.fedora_pkg.jinja2_reqformat(req)
        expected = 'rubygem(foo)'
        self.assertEqual(out, expected)

    def test_source0(self):
        expected = 'https://rubygems.org/gems/%{gem_name}-%{version}.gem'
        self.assertEqual(self.fedora_pkg.source0, expected)


if __name__ == '__main__':
    unittest.main()
