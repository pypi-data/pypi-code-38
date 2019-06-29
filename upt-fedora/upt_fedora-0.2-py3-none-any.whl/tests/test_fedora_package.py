# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import datetime
import unittest

import upt

from upt_fedora.upt_fedora import FedoraPackage


class TestFedoraPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '42', summary='summary',
                                   homepage='homepage')
        self.fedora_pkg = FedoraPackage(self.upt_pkg, None)

    def test_attributes(self):
        self.assertEqual(self.upt_pkg.version, self.fedora_pkg.version)
        self.assertEqual(self.upt_pkg.summary, self.fedora_pkg.summary)
        self.assertEqual(self.upt_pkg.homepage, self.fedora_pkg.homepage)

    def test_licenses(self):
        # No licenses
        self.upt_pkg.licenses = []
        self.assertEqual(self.fedora_pkg.licenses, '')

        # A single good license
        self.upt_pkg.licenses = [upt.licenses.ApacheLicenseTwoDotZero()]
        self.assertEqual(self.fedora_pkg.licenses, 'ASL 2.0')

        # A single bad license
        self.upt_pkg.licenses = [upt.licenses.AdaptivePublicLicense()]
        self.assertEqual(self.fedora_pkg.licenses, 'BAD LICENSE (APL-1.0)')

        # A mix of good and bad licenses
        self.upt_pkg.licenses = [
            upt.licenses.ApacheLicenseTwoDotZero(),
            upt.licenses.AdaptivePublicLicense()
        ]
        self.assertEqual(self.fedora_pkg.licenses,
                         'BAD LICENSE (Apache-2.0 APL-1.0)')

    def test_today(self):
        # We cannot mock datetime.datetime.today, because built-in types are
        # immutable. We subclass datetime.datetime and redefine "today"
        # instead.
        class MockDatetime(datetime.datetime):
            def today():
                return datetime.datetime(1989, 5, 26)

        datetime.datetime = MockDatetime
        self.assertEqual(self.fedora_pkg.today(), 'Fri May 26 1989')

    def test_depends(self):
        self.assertListEqual(self.fedora_pkg.build_depends, [])
        self.assertListEqual(self.fedora_pkg.run_depends, [])
        self.assertListEqual(self.fedora_pkg.test_depends, [])

        requirements = {
            'build': [upt.PackageRequirement('foo')],
            'run': [upt.PackageRequirement('bar')],
            'test': [upt.PackageRequirement('baz')],
        }
        self.upt_pkg.requirements = requirements
        self.assertListEqual(self.fedora_pkg.build_depends,
                             requirements['build'])
        self.assertListEqual(self.fedora_pkg.run_depends,
                             requirements['run'])
        self.assertListEqual(self.fedora_pkg.test_depends,
                             requirements['test'])


if __name__ == '__main__':
    unittest.main()
