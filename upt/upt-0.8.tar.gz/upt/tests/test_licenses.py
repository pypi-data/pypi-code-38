# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest
from unittest import mock

from upt import licenses


class TestLicenses(unittest.TestCase):
    def test_simple_license(self):
        class TestLicense(licenses.License):
            pass
        license = TestLicense()
        self.assertFalse(license.is_osi_approved())
        self.assertFalse(license.is_gpl_compatible())
        self.assertFalse(license.is_dfsg_compatible())

    def test_osi_approved_license(self):
        class TestLicense(licenses.OSIApprovedLicense):
            pass
        license = TestLicense()
        self.assertTrue(license.is_osi_approved())
        self.assertFalse(license.is_gpl_compatible())

    def test_gpl_compatible_license(self):
        class TestLicense(licenses.GPLCompatibleLicense):
            pass
        license = TestLicense()
        self.assertFalse(license.is_osi_approved())
        self.assertTrue(license.is_gpl_compatible())

    def test_dfsg_compatible_license(self):
        class TestLicense(licenses.DFSGCompatibleLicense):
            pass
        license = TestLicense()
        self.assertFalse(license.is_osi_approved())
        self.assertFalse(license.is_gpl_compatible())
        self.assertTrue(license.is_dfsg_compatible())

    def test_osi_gpl_dfsg_license(self):
        class TestLicense(licenses.DFSGCompatibleLicense,
                          licenses.GPLCompatibleLicense,
                          licenses.OSIApprovedLicense):
            pass
        license = TestLicense()
        self.assertTrue(license.is_dfsg_compatible())
        self.assertTrue(license.is_gpl_compatible())
        self.assertTrue(license.is_osi_approved())

    @mock.patch('spdx_lookup.match')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='')
    def test_guess_from_file(self, open_fn, match_fn):
        # Invalid arguments
        with self.assertRaises(ValueError):
            licenses.guess_from_file('/some/path', min_confidence=-1)

        with self.assertRaises(ValueError):
            licenses.guess_from_file('/some/path', min_confidence=101)

        # spdx_lookup cannot find anything
        match_fn.return_value = None
        self.assertIsInstance(licenses.guess_from_file('/some/path'),
                              licenses.UnknownLicense)

        match = mock.Mock(confidence=50, license=mock.Mock(id='BSD-3-Clause'))
        match_fn.return_value = match
        self.assertIsInstance(licenses.guess_from_file('/some/path'),
                              licenses.UnknownLicense)

        match = mock.Mock(confidence=100, license=mock.Mock(id='BSD-3-Clause'))
        match_fn.return_value = match
        self.assertIsInstance(licenses.guess_from_file('/some/path'),
                              licenses.BSDThreeClauseLicense)

    def test_equality(self):
        self.assertEqual(licenses.BSDThreeClauseLicense(),
                         licenses.BSDThreeClauseLicense())

        self.assertNotEqual(licenses.BSDTwoClauseLicense(),
                            licenses.BSDThreeClauseLicense())
