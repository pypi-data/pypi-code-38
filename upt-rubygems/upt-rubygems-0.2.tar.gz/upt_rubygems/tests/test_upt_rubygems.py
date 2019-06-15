# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import requests_mock

import upt
from upt_rubygems.upt_rubygems import RubyGemsFrontend


class TestRubyGemsFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = RubyGemsFrontend()
        self.pkg_name = 'foo'
        self.url = f'https://rubygems.org/api/v1/gems/{self.pkg_name}.json'

    @requests_mock.mock()
    def test_licenses_not_defined(self, requests):
        requests.get(self.url, json={'licenses': None})
        pkg = self.frontend.parse(self.pkg_name)
        self.assertEqual(pkg.licenses, [])

    @requests_mock.mock()
    def test_licenses_defined(self, requests):
        requests.get(self.url, json={'licenses': ['Ruby']})
        pkg = self.frontend.parse(self.pkg_name)
        self.assertEqual(pkg.licenses, [upt.licenses.RubyLicense()])


class TestLicenses(unittest.TestCase):
    def setUp(self):
        self.frontend = RubyGemsFrontend()

    def test_no_license(self):
        out = self.frontend._guess_licenses([])
        expected = []
        self.assertListEqual(out, expected)

    def test_one_license(self):
        out = self.frontend._guess_licenses(['Ruby'])
        expected = [upt.licenses.RubyLicense()]
        self.assertListEqual(out, expected)

        out = self.frontend._guess_licenses(['same as Ruby'])
        expected = [upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)

    def test_multiple_licenses(self):
        out = self.frontend._guess_licenses(['Ruby', 'same as Ruby'])
        expected = [upt.licenses.RubyLicense(), upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)


class TestRequirements(unittest.TestCase):
    def setUp(self):
        self.frontend = RubyGemsFrontend()

    def test_empty_requirements(self):
        expected = {}
        out = self.frontend._get_requirements({})
        self.assertEqual(out, expected)

    def test_runtime_requirements(self):
        json_reqs = {
            'runtime': [{
                'name': 'foo',
                'requirements': '> 0.12',
            }, {
                'name': 'bar',
                'requirements': '>= 13.37',
            }]
        }
        expected = {
            'run': [upt.PackageRequirement('foo', '> 0.12'),
                    upt.PackageRequirement('bar', '>= 13.37')]
        }
        out = self.frontend._get_requirements(json_reqs)
        self.assertDictEqual(out, expected)

    def test_development_requirements(self):
        json_reqs = {
            'development': [{
                'name': 'baz',
                'requirements': '> 42',
            }]
        }
        expected = {
            'test': [upt.PackageRequirement('baz', '> 42')]
        }
        out = self.frontend._get_requirements(json_reqs)
        self.assertDictEqual(out, expected)

    def test_runtime_development_requirements(self):
        json_reqs = {
            'runtime': [{
                'name': 'foo',
                'requirements': '> 0.12',
            }, {
                'name': 'bar',
                'requirements': '>= 13.37',
            }],
            'development': [{
                'name': 'baz',
                'requirements': '> 42',
            }]
        }
        expected = {
            'run': [upt.PackageRequirement('foo', '> 0.12'),
                    upt.PackageRequirement('bar', '>= 13.37')],
            'test': [upt.PackageRequirement('baz', '> 42')],
        }
        out = self.frontend._get_requirements(json_reqs)
        self.assertDictEqual(out, expected)

    def test_requirements_with_twiddle_wakka(self):
        json_reqs = {
            'runtime': [{
                'name': 'foo',
                'requirements': '~> 0.12',
            }, {
                'name': 'bar',
                'requirements': '>= 1.0.1, ~> 1.0'
            }]
        }
        expected = {
            'run': [upt.PackageRequirement('foo', '>=0.12,<1.0'),
                    upt.PackageRequirement('bar', '>= 1.0.1,>=1.0,<2.0')]
        }
        out = self.frontend._get_requirements(json_reqs)
        self.assertDictEqual(out, expected)

    def test_requirements_with_bugged_twiddle_wakka(self):
        json_reqs = {
            'runtime': [{
                'name': 'foo',
                'requirements': '~> 0.12.1.a',
            }]
        }
        expected = {}
        out = self.frontend._get_requirements(json_reqs)
        self.assertDictEqual(out, expected)

    def test_fix_twiddle_wakka_expr(self):
        results = [
            ('>= 1.2', '>= 1.2'),
            ('~> 0', '>=0,<1'),
            ('~> 2.2', '>=2.2,<3.0'),
            ('~> 2.2.0', '>=2.2.0,<2.3.0'),
        ]
        for specifier, expected in results:
            self.assertEqual(self.frontend._fix_twiddle_wakka_expr(specifier),
                             expected)

    def test_fix_twiddle_wakka_bugged_expr(self):
        # Pre-releases are not allowed when using the twiddle-wakka operator.
        with self.assertRaises(ValueError):
            self.frontend._fix_twiddle_wakka_expr('~> 2.0.0.a')


class TestArchives(unittest.TestCase):
    def setUp(self):
        self.frontend = RubyGemsFrontend()

    def test_no_archive(self):
        self.assertEqual(self.frontend._get_archives({}), [])

    def test_no_sha(self):
        json = {
            'gem_uri': 'some_uri',
        }
        archives = self.frontend._get_archives(json)
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].url, 'some_uri')


if __name__ == '__main__':
    unittest.main()
