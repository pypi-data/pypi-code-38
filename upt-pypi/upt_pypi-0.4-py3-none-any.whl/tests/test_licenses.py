# Copyright 2019      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from unittest import mock
import unittest

import upt
from upt_pypi.upt_pypi import PyPIFrontend
from upt_pypi import licenses


class TestLicenses(unittest.TestCase):
    def setUp(self):
        self.frontend = PyPIFrontend()

    def test_classifiers_no_classifiers(self):
        out = licenses.guess_licenses_using_classifiers([])
        self.assertListEqual(out, [])

    def test_classifiers_simple_case(self):
        classifiers = [
            'License :: OSI Approved :: MIT License',
        ]
        out = licenses.guess_licenses_using_classifiers(classifiers)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_simple_case_with_invalid_license_classifier(self):
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'License :: OSI Approved :: MIT License',
        ]
        out = licenses.guess_licenses_using_classifiers(classifiers)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_license_field_valid_spdx_identifier(self):
        license_field = 'BSD-3-Clause'  # Valid SPDX identifier
        out = licenses.guess_licenses_using_license_field(license_field)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.BSDThreeClauseLicense)

    def test_license_field_weird_cases(self):
        license_field = 'mitlicense'
        out = licenses.guess_licenses_using_license_field(license_field)
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_guess_licenses_simple_case(self):
        # The classifiers are enough
        fake_json = {
            'info': {
                'classifiers': [
                    'License :: OSI Approved :: MIT License',
                ]
            }
        }
        out = licenses.guess_licenses(fake_json, '')
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_guess_licenses_many_classifiers(self):
        # We get multiple licenses, this is a weird case, we want to let the
        # user decide.
        fake_json = {
            'info': {
                'classifiers': [
                    'License :: OSI Approved :: MIT License',
                    'License :: OSI Approved :: MIT License',
                ]
            }
        }
        out = licenses.guess_licenses(fake_json, '')
        self.assertEqual(len(out), 2)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)
        self.assertIsInstance(out[1], upt.licenses.MITLicense)

    def test_guess_licenses_no_classifiers_license_field(self):
        fake_json = {
            'info': {
                'license': 'MIT',
            }
        }
        out = licenses.guess_licenses(fake_json, '')
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_guess_licenses_no_classifiers_no_license_field(self):
        fake_json = {
            'info': {
            }
        }
        with mock.patch('upt_pypi.licenses.guess_licenses_from_sdist') as m:
            m.return_value = [
                upt.licenses.MITLicense()
            ]
            out = licenses.guess_licenses(fake_json, 'someurl')
            m.assert_called_once()
            self.assertEqual(len(out), 1)
            self.assertIsInstance(out[0], upt.licenses.MITLicense)

    def test_guess_licenses_no_classifiers_no_license_field_no_sdist(self):
        fake_json = {
            'info': {
            }
        }
        out = licenses.guess_licenses(fake_json, '')
        self.assertListEqual(out, [])

    def test_guess_licenses_no_classifiers_no_license_field_weird_sdist(self):
        fake_json = {
            'info': {
            }
        }
        out = licenses.guess_licenses(fake_json, 'some-weird-archive.weird')
        self.assertListEqual(out, [])


if __name__ == '__main__':
    unittest.main()
