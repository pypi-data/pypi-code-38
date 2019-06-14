# -*- coding: utf-8 -*-
#
# Copyright (c) 2019  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from mock import patch, mock_open, MagicMock

from odcs.server.mock_runroot import (
    mock_runroot_init, raise_if_runroot_key_invalid, mock_runroot_run,
    mock_runroot_install, rmtree_skip_mounts)
from .utils import AnyStringWith


class TestMockRunroot(unittest.TestCase):

    def setUp(self):
        super(TestMockRunroot, self).setUp()

    def tearDown(self):
        super(TestMockRunroot, self).tearDown()

    @patch("odcs.server.mock_runroot.create_koji_session")
    @patch("odcs.server.mock_runroot.execute_mock")
    @patch("odcs.server.mock_runroot.print", create=True)
    @patch("odcs.server.mock_runroot.rmtree_skip_mounts")
    def test_mock_runroot_init(
            self, rmtree_skip_mounts, fake_print, execute_mock, create_koji_session):
        execute_mock.side_effect = RuntimeError("Expected exception")
        koji_session = create_koji_session.return_value
        koji_session.getRepo.return_value = {"id": 1}

        m = mock_open()
        with patch('odcs.server.mock_runroot.open', m, create=True):
            with self.assertRaises(RuntimeError):
                mock_runroot_init("f30-build")

        fake_print.assert_called_once()
        m.return_value.write.assert_called_once_with(AnyStringWith("f30-build"))

        execute_mock.assert_called_once_with(AnyStringWith("-"), ['--init'])
        rmtree_skip_mounts.assert_called_once()

    def test_raise_if_runroot_key_invalid(self):
        with self.assertRaises(ValueError):
            raise_if_runroot_key_invalid("../../test")
        with self.assertRaises(ValueError):
            raise_if_runroot_key_invalid("/tmp")
        with self.assertRaises(ValueError):
            raise_if_runroot_key_invalid("x.cfg")
        raise_if_runroot_key_invalid("1-2-3-4-a-s-d-f")

    @patch("odcs.server.mock_runroot.execute_mock")
    @patch("odcs.server.mock_runroot.execute_cmd")
    def test_mock_runroot_run(self, execute_cmd, execute_mock):
        mock_runroot_run("foo-bar", ["df", "-h"])

        execute_mock.assert_called_once_with('foo-bar', [
            '--old-chroot', '--chroot', '--', '/bin/sh', '-c', '{ df -h; }'], False)
        execute_cmd.assert_any_call([
            'mount', '-o', 'bind', AnyStringWith('test_composes'), AnyStringWith('test_composes')])
        execute_cmd.assert_any_call(['umount', '-l', AnyStringWith('test_composes')])

    @patch("odcs.server.mock_runroot.execute_mock")
    def test_mock_runroot_install(self, execute_mock):
        mock_runroot_install("foo-bar", ["lorax", "dracut"])
        execute_mock.assert_called_once_with('foo-bar', ['--install', 'lorax', 'dracut'])

    @patch("odcs.server.mock_runroot.execute_mock")
    @patch("odcs.server.mock_runroot.rmtree_skip_mounts")
    def test_mock_runroot_install_exception(self, rmtree_skip_mounts, execute_mock):
        execute_mock.side_effect = RuntimeError("Expected exception")
        with self.assertRaises(RuntimeError):
            mock_runroot_install("foo-bar", ["lorax", "dracut"])
        rmtree_skip_mounts.assert_called_once()

    @patch("odcs.server.mock_runroot.os.rmdir")
    @patch("odcs.server.mock_runroot.os.listdir")
    @patch("odcs.server.mock_runroot.os.lstat")
    @patch("odcs.server.mock_runroot.os.remove")
    @patch("odcs.server.mock_runroot.stat.S_ISDIR")
    def test_mock_runroot_rmtree(self, isdir, remove, lstat, listdir, rmdir):
        """
        Tests that `rmtree_skip_mounts` really skips the mount points when
        removing the runroot root directory.

        The fake runroot root directory in this test is following:
        - /mnt/koji - empty directory which should be removed
        - /mnt/odcs - non-empty mountpoint directory must not be removed.
        - /x - regular file which should be removed.
        """
        def mocked_listdir(path):
            # Creates fake directory structure within the /var/lib/mock/foo-bar/root:
            #  - /mnt/koji
            #  - /mnt/odcs/foo
            #  - /x
            if path == "/var/lib/mock/foo-bar/root":
                return ["mnt", "x"]
            if path.endswith("/mnt"):
                return ["odcs", "koji"]
            elif path.endswith("/odcs"):
                return ["foo"]
            return []
        listdir.side_effect = mocked_listdir

        def mocked_isdir(mode):
            # We use fake values here:
            # - 0 means it is not a directory.
            # - 1 means it is a directory.
            return mode
        isdir.side_effect = mocked_isdir

        def mocked_lstat(path):
            stat_result = MagicMock()
            if path.endswith("/x"):
                stat_result.st_mode = 0  # Just fake return value for regular file.
            else:
                stat_result.st_mode = 1  # Fake value for directory.
            return stat_result
        lstat.side_effect = mocked_lstat

        rmtree_skip_mounts("/var/lib/mock/foo-bar/root", ["/mnt/odcs"])

        rmdir.assert_called_once_with("/var/lib/mock/foo-bar/root/mnt/koji")
        remove.assert_called_once_with("/var/lib/mock/foo-bar/root/x")
