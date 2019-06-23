# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from unittest import mock
import unittest

import upt
from upt import PackageRequirement
from upt_pypi.upt_pypi import PyPIFrontend


class TestPyPIFrontend(unittest.TestCase):
    def setUp(self):
        self.parser = PyPIFrontend()

    def test_string_req_to_upt_req(self):
        out = self.parser._string_req_to_upt_pkg_req('cryptography')
        expected = upt.PackageRequirement('cryptography', '')
        self.assertEqual(out, expected)

        out = self.parser._string_req_to_upt_pkg_req('cryptography (>=1.3.4)')
        expected = upt.PackageRequirement('cryptography', '>=1.3.4')
        self.assertEqual(out, expected)

    def test_string_req_list_to_upt_req_list(self):
        out = self.parser._string_req_list_to_upt_pkg_req_list([])
        expected = []
        self.assertListEqual(out, expected)

        reqs = ['foo (>1.0)', 'bar']
        out = self.parser._string_req_list_to_upt_pkg_req_list(reqs)
        expected = [
            upt.PackageRequirement('foo', '>1.0'),
            upt.PackageRequirement('bar', '')
        ]
        self.assertListEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    def test_compute_requirements_no_requires_dist(self, m):
        """PyPI does not provide the requires_dist field in the JSON."""
        self.parser.json = {
            'info': {'version': '1.2'},
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
        }
        expected = {'run': [upt.PackageRequirement('foo', '')]}
        m.return_value = expected
        out = self.parser.compute_requirements()
        self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    def test_compute_requirements_null_requires_dist(self, m):
        """PyPI provides the requires_dist field, but it is None."""
        self.parser.json = {
            'info': {'version': '1.2'},
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
            'required_dist': None,
        }
        expected = {'run': [upt.PackageRequirement('foo', '')]}
        m.return_value = expected
        out = self.parser.compute_requirements()
        self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    def test_compute_requirements_full_requires_dist(self, m):
        """Perfect case: requires_dist has both runtime and tests reqs."""
        self.parser.json = {
            'info': {
                'version': '1.2',
                'requires_dist': [
                    "foo; extra == 'somefeature'",
                    "bar; whatever",
                    "requests-mock; extra == 'test'",
                    "upt (>=0.2)"
                ],
            },
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
        }
        expected = {
            'run': [upt.PackageRequirement('upt', '>=0.2')],
            'test': [upt.PackageRequirement('requests-mock', '')],
        }
        out = self.parser.compute_requirements()
        m.assert_not_called()
        self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    def test_compute_requirements_only_runtime_fallback(self, m):
        """Requires_dist provides only the runtime dependencies.

        We need to inspect the wheel.
        """
        self.parser.json = {
            'info': {
                'version': '1.2',
                'requires_dist': [
                    "upt (>=0.2)"
                ],
            },
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
        }
        expected = {
            'run': [upt.PackageRequirement('upt', '>=0.2')],
            'test': [upt.PackageRequirement('requests-mock', '')],
        }
        m.return_value = expected
        out = self.parser.compute_requirements()
        self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'get_wheel_url')
    def test_compute_requirements_only_runtime_no_wheel(self, get_wheel_url_m):
        """Requires_dist provides only the runtime dependencies.

        To make things more complex, there is no available wheel.
        We want to fallback to what was found using requires_dist.
        """
        self.parser.json = {
            'info': {
                'version': '1.2',
                'requires_dist': [
                    "upt (>=0.2)"
                ],
            },
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
        }
        expected = {
            'run': [upt.PackageRequirement('upt', '>=0.2')],
        }
        get_wheel_url_m.side_effect = ValueError()
        out = self.parser.compute_requirements()
        self.assertDictEqual(out, expected)

    @mock.patch.object(PyPIFrontend, 'compute_requirements_from_wheel')
    def test_compute_requirements_only_runtime_empty_wheel(self, m):
        """Requires_dist provides only the runtime dependencies.

        In this scenario, the available wheel returns an empty list for both
        the runtime and test dependencies.
        """
        self.parser.json = {
            'info': {
                'version': '1.2',
                'requires_dist': [
                    "upt (>=0.2)"
                ],
            },
            'releases': {'1.2': [{
                'packagetype': 'bdist_wheel',
                'url': 'https://whatever'
            }]},
        }
        deps_from_wheel = {
            'run': [],
            'test': [],
        }
        m.return_value = deps_from_wheel

        expected = {
            'run': [upt.PackageRequirement('upt', '>=0.2')],
        }
        out = self.parser.compute_requirements()
        self.assertDictEqual(out, expected)

    def test_compute_requirements_invalid_json(self):
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data='{}'):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
        self.assertEqual(reqs, {})

    def test_compute_requirements_no_requirements(self):
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data='{}'):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertEqual(reqs, {})

    def test_compute_requirements_from_metadata_json(self):
        data = '''\
{
   "run_requires": [
      {
         "requires": [
            "foo (>3.14)",
            "bar"
         ]
      }
    ],
   "test_requires": [
      {
         "requires": [
            "pytest"
         ]
      }
    ]
}'''
        expected = {
            'run': [
                PackageRequirement('foo', '>3.14'),
                PackageRequirement('bar', '')
            ],
            'test': [
                PackageRequirement('pytest', '')
            ],
        }
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data=data):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertDictEqual(reqs, expected)

    def test_compute_requirements_from_metadata_json_ignore_extras(self):
        data = '''\
{
   "run_requires": [
      {
         "requires": [
            "foo (>3.14)",
            "bar"
         ]
      },
      {
         "extra": "some-nice-feature",
         "requires": [
            "baz"
         ]
      }
    ]
}'''
        expected = {
            'run': [
                PackageRequirement('foo', '>3.14'),
                PackageRequirement('bar', '')
            ]
        }
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data=data):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertDictEqual(reqs, expected)


class TestArchiveMethods(unittest.TestCase):
    def setUp(self):
        self.frontend = PyPIFrontend()
        self.release = [{
            'url': 'http://example.com/source.tar.gz',
            'packagetype': 'sdist',
            'size': 123,
            'digests': {
                'md5': 'md5',
                'sha256': 'sha256',
            }
        }, {
            'url': 'http://example.com/wheel.whl',
            'packagetype': 'bdist_wheel',
            'size': 321,
            'digests': {
                'md5': 'md5-wheel',
                'sha256': 'sha256-wheel',
            }
        }]

    def test_get_archive_info_bad_type(self):
        with self.assertRaises(ValueError):
            self.frontend.get_archive_info(self.release, 'bad-argument')

    def test_get_archive_sdist(self):
        self.assertEqual(self.frontend.get_sdist_archive_url(self.release),
                         self.release[0]['url'])

    def test_get_archive_bdist(self):
        self.assertEqual(self.frontend.get_wheel_url(self.release),
                         self.release[1]['url'])

    def test_get_archives(self):
        out = self.frontend.get_archives(self.release)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].url, 'http://example.com/source.tar.gz')
        self.assertEqual(out[0].size, 123)
        self.assertEqual(out[0].md5, 'md5')
        self.assertEqual(out[0].sha256, 'sha256')


if __name__ == '__main__':
    unittest.main()
