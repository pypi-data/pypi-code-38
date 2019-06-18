# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from io import StringIO
import unittest
from unittest import mock
import sys

import upt


class TestPackage(unittest.TestCase):
    def test_str(self):
        pkg = upt.Package('foo', '4.2')
        self.assertEqual(str(pkg), 'foo@4.2')

        pkg = upt.Package('foo', '4.2')
        self.assertNotEqual(str(pkg), 'foo@42')

    def test_get_archive_none_available(self):
        error = 'No such archive could be found'
        pkg = upt.Package('foo', '4.2', archives=[])
        with self.assertRaisesRegex(upt.ArchiveUnavailable, error):
            pkg.get_archive()

    def test_get_archive(self):
        archives = [
            upt.Archive('url')
        ]
        pkg = upt.Package('foo', '4.2', archives=archives)
        self.assertEqual(pkg.get_archive(), archives[0])

    def test_get_archive_with_argument(self):
        archives = [
            upt.Archive('url', archive_type=upt.ArchiveType.RUBYGEM)
        ]
        pkg = upt.Package('foo', '4.2', archives=archives)
        with self.assertRaises(upt.ArchiveUnavailable):
            pkg.get_archive()
        self.assertEqual(pkg.get_archive(upt.ArchiveType.RUBYGEM), archives[0])

    @mock.patch('os.remove')
    def test_clean_archive_downloaded(self, remove_fn):
        archives = [
            upt.Archive('url')
        ]
        archives[0]._filepath = '/fake/path'  # Archive 'downloaded'
        pkg = upt.Package('foo', '4.2', archives=archives)
        pkg._clean()
        remove_fn.assert_called_once_with('/fake/path')

    @mock.patch('os.remove')
    def test_clean_archive_not_downloaded(self, remove_fn):
        archives = [
            upt.Archive('url')
        ]
        pkg = upt.Package('foo', '4.2', archives=archives)
        pkg._clean()
        remove_fn.assert_not_called()


class TestPackageRequirement(unittest.TestCase):
    def test_str_with_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo', '>3.14')
        self.assertEqual(str(pkg_req), 'foo (>3.14)')

    def test_str_without_specifier(self):
        pkg_req = upt.upt.PackageRequirement('foo')
        self.assertEqual(str(pkg_req), 'foo')

    def test_equality(self):
        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('foo', '>3.14')
        self.assertEqual(pkg_req_a, pkg_req_b)

        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('foo', '>13.37')
        self.assertNotEqual(pkg_req_a, pkg_req_b)

        pkg_req_a = upt.upt.PackageRequirement('foo', '>3.14')
        pkg_req_b = upt.upt.PackageRequirement('bar', '>3.14')
        self.assertNotEqual(pkg_req_a, pkg_req_b)


class TestUtils(unittest.TestCase):
    @mock.patch('pkg_resources.iter_entry_points')
    def test_get_installed_plugins(self, m_iter_entry_points):
        plugin = mock.Mock()
        plugin_cls = mock.Mock()
        plugin_cls.name = 'fake-name'
        plugin.load.return_value = plugin_cls
        m_iter_entry_points.return_value = [plugin]
        self.assertDictEqual(upt.upt._get_installed_plugins('dummy'),
                             {'fake-name': plugin.load.return_value})

    @mock.patch('upt.upt._get_installed_plugins')
    def test_get_installed_frontends_backends(self, m_get_plugins):
        fake_frontends = {
            'fake-frontend': mock.Mock()
        }

        fake_backends = {
            'fake-backend': mock.Mock()
        }

        def get_plugins(entrypoint):
            if entrypoint == 'upt.frontends':
                return fake_frontends
            elif entrypoint == 'upt.backends':
                return fake_backends
            else:
                raise ValueError(entrypoint)

        m_get_plugins.side_effect = get_plugins
        self.assertDictEqual(upt.upt._get_installed_frontends(),
                             fake_frontends)
        self.assertDictEqual(upt.upt._get_installed_backends(),
                             fake_backends)


class TestParser(unittest.TestCase):
    def test_package_single_frontend(self):
        parser = upt.upt.create_parser(['pypi'], ['guix', 'nix'])
        args = 'package -b guix requests'.split()
        parser.parse_args(args)

    def test_package_single_backend(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix'])
        args = 'package -f pypi requests'.split()
        parser.parse_args(args)

    def test_package_missing_frontend(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix', 'nix'])
        args = 'package -b guix requests'.split()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)

    def test_package_missing_backend(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix', 'nix'])
        args = 'package -f pypi requests'.split()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)

    def test_package_missing_frontend_and_backend(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix', 'nix'])
        args = 'package requests'.split()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)

    def test_package_missing_package(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix', 'nix'])
        args = 'package -f pypi -b guix'.split()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)

    def test_package_exclusive_logging_options(self):
        parser = upt.upt.create_parser(['cpan', 'pypi'], ['guix', 'nix'])
        args = 'package -f pypi -b guix --debug --quiet requests'.split()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        sys.argv = ['/path/to/upt']

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_no_args(self, m_stdout, m_stderr):
        with self.assertRaises(SystemExit):
            upt.upt.main()
        self.assertEqual(m_stdout.getvalue(), '')
        self.assertEqual(m_stderr.getvalue()[:6], 'usage:')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('upt.upt._get_installed_backends')
    def test_list_backends(self, m_get_backends, m_stdout, m_stderr):
        sys.argv.append('list-backends')
        m_get_backends.return_value = {
            'fake-backend-1': object(),
            'fake-backend-2': object(),
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(m_stdout.getvalue(),
                         'fake-backend-1\nfake-backend-2\n')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('upt.upt._get_installed_frontends')
    def test_list_frontends(self, m_get_frontends, m_stdout, m_stderr):
        sys.argv.append('list-frontends')
        m_get_frontends.return_value = {
            'fake-frontend-1': object(),
            'fake-frontend-2': object(),
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(m_stdout.getvalue(),
                         'fake-frontend-1\nfake-frontend-2\n')
        self.assertEqual(m_stderr.getvalue(), '')

    @mock.patch('upt.upt._get_installed_frontends', return_value={})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid': mock.Mock()})
    def test_package_no_frontends(self, m_backends, m_frontends):
        sys.argv.extend('package'.split())
        with self.assertRaises(SystemExit):
            upt.upt.main()

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends', return_value={})
    def test_package_no_backends(self, m_backends, m_frontends):
        sys.argv.extend('package'.split())
        with self.assertRaises(SystemExit):
            upt.upt.main()

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid-backend': mock.Mock()})
    def test_package_invalid_frontend(self, m_backends, m_frontends):
        sys.argv.extend('package -f invalid -b valid-backend pkgname'.split())
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 2)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid-backend': mock.Mock()})
    def test_package_invalid_backend(self, m_backends, m_frontends):
        sys.argv.extend('package -f valid-frontend -b invalid pkgname'.split())
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 2)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid-backend': mock.Mock()})
    def test_package_unhandled_frontend(self, m_backends, m_frontends):
        cmdline = 'package -f valid-frontend -b valid-backend pkgname'
        sys.argv.extend(cmdline.split())

        def backend_fail(*args, **kwargs):
            raise upt.exceptions.UnhandledFrontendError('valid-backend',
                                                        'valid-frontend')
        fake_backend = mock.Mock()
        fake_backend().create_package.side_effect = backend_fail
        m_backends.return_value = {
            'valid-backend': fake_backend
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)

    @mock.patch('upt.upt._get_installed_frontends',
                return_value={'valid-frontend': mock.Mock()})
    @mock.patch('upt.upt._get_installed_backends',
                return_value={'valid-backend': mock.Mock()})
    def test_package_invalid_pkgname(self, m_backends, m_frontends):
        cmdline = 'package -f valid-frontend -b valid-backend pkgname'
        sys.argv.extend(cmdline.split())

        def frontend_fail(*args, **kwargs):
            raise upt.exceptions.InvalidPackageNameError('valid-backend',
                                                         'pkgname')
        fake_frontend = mock.Mock()
        fake_frontend().parse.side_effect = frontend_fail
        m_frontends.return_value = {
            'valid-frontend': fake_frontend
        }
        with self.assertRaises(SystemExit) as exit:
            upt.upt.main()
        self.assertEqual(exit.exception.code, 1)


class TestArchive(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('os.stat', return_value=mock.Mock(st_size=42))
    def test_size(self, stat_fn):
        archive = upt.Archive('url', size=0)
        archive._filepath = '/fake/path'
        self.assertEqual(archive.size, 42)

        archive = upt.Archive('url', size=12)
        archive._filepath = '/fake/path'
        self.assertEqual(archive.size, 12)

    def test_filename(self):
        archive = upt.Archive('http://example.com/source.tar.gz')
        self.assertEqual(archive.filename, 'source.tar.gz')

    @mock.patch('urllib.request.urlretrieve',
                return_value=('/tmpdir/source.tar.gz', None))
    @mock.patch('tempfile.gettempdir', return_value='/tmpdir')
    def test_filepath(self, gettempdir_fn, urlretrieve_fn):
        archive = upt.Archive('http://example.com/source.tar.gz')
        self.assertEqual(archive.filepath, '/tmpdir/source.tar.gz')

    @mock.patch('upt.checksum.compute_checksum', return_value='hash-output')
    @mock.patch('urllib.request.urlretrieve',
                return_value=('/tmpdir/source.tar.gz', None))
    @mock.patch('tempfile.gettempdir', return_value='/tmpdir')
    def test_checksum(self, gettmpdir_fn, urlretrieve_fn, compute_checksum_fn):
        archive = upt.Archive('http://example.com/source.tar.gz')
        self.assertEqual(archive._checksum('fake-hash'), 'hash-output')
        self.assertEqual(archive._checksum('fake-hash'), 'hash-output')
        urlretrieve_fn.assert_called_once()
        compute_checksum_fn.assert_called_once()

    @mock.patch('upt.checksum.compute_checksum', return_value='hash-output')
    def test_checksums_provided(self, compute_checksum_fn):
        archive = upt.Archive('url', md5='md5', rmd160='rmd160',
                              sha256='sha256', sha256_base64='sha256_base64')
        self.assertEqual(archive.md5, 'md5')
        self.assertEqual(archive.rmd160, 'rmd160')
        self.assertEqual(archive.sha256, 'sha256')
        self.assertEqual(archive.sha256_base64, 'sha256_base64')
        compute_checksum_fn.assert_not_called()
