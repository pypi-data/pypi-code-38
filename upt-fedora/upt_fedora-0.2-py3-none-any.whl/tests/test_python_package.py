# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_fedora.upt_fedora import FedoraPythonPackage


class TestPythonPackage(unittest.TestCase):
    def setUp(self):
        upt_pkg = upt.Package('foo', '42')
        self.fedora_pkg = FedoraPythonPackage(upt_pkg, None)

    def test_name(self):
        upt_pkg = upt.Package('foo', '42')
        fedora_pkg = FedoraPythonPackage(upt_pkg, None)
        self.assertEqual(fedora_pkg.name, 'python-foo')

        upt_pkg = upt.Package('python-foo', '42')
        fedora_pkg = FedoraPythonPackage(upt_pkg, None)
        self.assertEqual(fedora_pkg.name, 'python-foo')

    def test_sourcename(self):
        sname = self.fedora_pkg._sourcename('foo')
        self.assertEqual(sname, 'foo')

        sname = self.fedora_pkg._sourcename('python-foo')
        self.assertEqual(sname, 'foo')

        self.assertEqual(self.fedora_pkg.sourcename, 'foo')

    def test_jinja2_reqformat(self):
        req = upt.PackageRequirement('foo', '>=1.0')

        out = self.fedora_pkg.jinja2_reqformat(req, 2)
        expected = 'python2-foo >=1.0'
        self.assertEqual(out, expected)

        out = self.fedora_pkg.jinja2_reqformat(req, 3)
        expected = 'python%{python3_pkgversion}-foo >=1.0'
        self.assertEqual(out, expected)

    def test_jinja2_reqformat_no_specifier(self):
        req = upt.PackageRequirement('foo')

        out = self.fedora_pkg.jinja2_reqformat(req, 2)
        expected = 'python2-foo'
        self.assertEqual(out, expected)

        out = self.fedora_pkg.jinja2_reqformat(req, 3)
        expected = 'python%{python3_pkgversion}-foo'
        self.assertEqual(out, expected)

    def test_source0(self):
        self.assertEqual(self.fedora_pkg.source0, '%pypi_source')


if __name__ == '__main__':
    unittest.main()
