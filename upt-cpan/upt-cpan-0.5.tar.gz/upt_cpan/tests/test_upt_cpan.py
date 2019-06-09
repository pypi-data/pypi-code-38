# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import requests_mock

import upt
from upt_cpan.upt_cpan import CPANFrontend


class TestCPANFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()

    def test_invalid_package_name(self):
        with self.assertRaises(upt.InvalidPackageNameError):
            self.frontend.parse('probably-invalid-package-name')

    def test_get_homepage(self):
        out = self.frontend._get_homepage({})
        self.assertIsNone(out)

        out = self.frontend._get_homepage({'homepage': 'foo'})
        self.assertEqual(out, 'foo')

        out = self.frontend._get_homepage({'bugtracker': {'web': 'foo'}})
        self.assertEqual(out, 'foo')

        out = self.frontend._get_homepage({'repository': {'web': 'foo'}})
        self.assertEqual(out, 'foo')

        json = {'repository': {'web': 'bar'}, 'homepage': 'foo'}
        out = self.frontend._get_homepage(json)
        self.assertEqual(out, 'foo')


class TestCPANJson(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()
        self.url = 'https://fastapi.metacpan.org/v1/release/perl-foo'

    @requests_mock.mock()
    def test_missing_metadata(self, requests):
        requests.get(self.url, json={})
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.version, '')
        self.assertEqual(pkg.summary, '')

    @requests_mock.mock()
    def test_missing_version(self, requests):
        json = {
            'metadata': {
                'abstract': 'foo bar baz'
            }
        }
        requests.get(self.url, json=json)
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.version, '')

    @requests_mock.mock()
    def test_missing_abstract(self, requests):
        json = {
        }
        requests.get(self.url, json=json)
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.summary, '')

    @requests_mock.mock()
    def test_missing_license(self, requests):
        requests.get(self.url, json={})
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.licenses, [])


class TestLicenses(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()

    def test_no_licenses(self):
        self.assertEqual(self.frontend._get_licenses([]), [])

    def test_one_license(self):
        out = self.frontend._get_licenses(['bsd'])
        expected = [upt.licenses.BSDThreeClauseLicense()]
        self.assertListEqual(out, expected)

        out = self.frontend._get_licenses(['whatever'])
        expected = [upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)

    def test_multiple_licenses(self):
        out = self.frontend._get_licenses(['freebsd', 'whatever'])
        expected = [upt.licenses.BSDTwoClauseLicense(),
                    upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)


class TestRequirements(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()

    def test_requirements_no_prereqs(self):
        expected = {}
        out = self.frontend._get_requirements({})
        self.assertEqual(out, expected)

    def test_requirements_carp_assert_more(self):
        # Real example from
        # https://fastapi.metacpan.org/v1/release/Carp-Assert-More
        prereqs = {
            "runtime": {
                "requires": {
                    "Test::Exception": "0",
                    "Carp": "0",
                    "Carp::Assert": "0",
                    "Test::More": "0.18",
                    "Scalar::Util": "0"
                }
            },
            "configure": {
                "requires": {
                    "ExtUtils::MakeMaker": "0"
                }
            },
            "build": {
                "requires": {
                    "ExtUtils::MakeMaker": "0"
                }
            }
        }
        expected = {
            'run': [
                upt.PackageRequirement('Test::Exception', ''),
                upt.PackageRequirement('Carp', ''),
                upt.PackageRequirement('Carp::Assert', ''),
                upt.PackageRequirement('Test::More', '>=0.18'),
                upt.PackageRequirement('Scalar::Util', ''),
            ],
            'config': [
                upt.PackageRequirement('ExtUtils::MakeMaker', '')
            ],
            'build': [
                upt.PackageRequirement('ExtUtils::MakeMaker', '')
            ],
        }
        out = self.frontend._get_requirements(prereqs)
        self.assertEqual(out, expected)

    def test_requirements_appconfig(self):
        # Real example from
        # https://fastapi.metacpan.org/v1/release/AppConfig
        prereqs = {
            "build": {
                "requires": {
                    "ExtUtils::MakeMaker": "0"
                }
            },
            "test": {
                "requires": {
                    "Test::Pod": "1.0"
                }
            },
            "runtime": {
                "requires": {
                    "perl": "5.008008",
                    "Test::More": "0"
                }
            },
            "configure": {
                "requires": {
                    "ExtUtils::MakeMaker": "0"
                }
            }
        }
        expected = {
            'build': [
                upt.PackageRequirement('ExtUtils::MakeMaker', ''),
            ],
            'config': [
                upt.PackageRequirement('ExtUtils::MakeMaker', ''),
            ],
            'run': [
                upt.PackageRequirement('Test::More', ''),
            ],
            'test': [
                upt.PackageRequirement('Test::Pod', '>=1.0'),
            ],
        }
        out = self.frontend._get_requirements(prereqs)
        self.assertEqual(out, expected)


class TestArchives(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()
        self.json = {
            'download_url': 'http://www.example.com/source.tar.gz',
            'stat': {
                'size': 123,
            }
        }

    def test_get_archives(self):
        out = self.frontend._get_archives(self.json)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].url, 'http://www.example.com/source.tar.gz')
        self.assertEqual(out[0].size, 123)


if __name__ == '__main__':
    unittest.main()
