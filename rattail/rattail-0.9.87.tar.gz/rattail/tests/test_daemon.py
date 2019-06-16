# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import errno
import stat
import tempfile
from unittest import TestCase
from mock import patch, mock_open, call, DEFAULT

from rattail import daemon


class DaemonTests(TestCase):

    pidfile = '/tmp/test_rattail_daemon.pid'

    def test_init(self):
        d = daemon.Daemon(self.pidfile)
        self.assertEqual(d.pidfile, self.pidfile)
        self.assertEqual(d.stdin, os.devnull)
        self.assertEqual(d.stdout, os.devnull)
        self.assertEqual(d.stderr, os.devnull)

    def test_delpid(self):

        # normal delete
        with open(self.pidfile, 'w') as f:
            f.write('foo')
        self.assertTrue(os.path.exists(self.pidfile))
        d = daemon.Daemon(self.pidfile)
        d.delpid()
        self.assertFalse(os.path.exists(self.pidfile))

        # file doesn't exist (no error)
        d.delpid()

    @patch('sys.exit')
    @patch('sys.stderr')
    def test_start(self, stderr, exit_):
        d = daemon.Daemon(self.pidfile)
        with patch.object(d, 'daemonize') as daemonize:
            with patch.object(d, 'run') as run:

                # pidfile exists
                with open(self.pidfile, 'w') as f:
                    f.write('42\n')
                self.assertTrue(os.path.exists(self.pidfile))
                exit_.side_effect = RuntimeError
                self.assertRaises(RuntimeError, d.start)
                stderr.write.assert_called_once_with("pidfile /tmp/test_rattail_daemon.pid already exist. Daemon already running?\n")
                exit_.assert_called_once_with(1)
                self.assertFalse(daemonize.called)
                self.assertFalse(run.called)

                stderr.reset_mock()
                exit_.reset_mock()

                # no pidfile, no daemonize
                os.remove(self.pidfile)
                self.assertFalse(os.path.exists(self.pidfile))
                d.start(daemonize=False)
                self.assertFalse(stderr.write.called)
                self.assertFalse(exit_.called)
                self.assertFalse(d.daemonize.called)
                d.run.assert_called_once_with()

                d.run.reset_mock()

                # no pidfile, with daemonize
                self.assertFalse(os.path.exists(self.pidfile))
                d.start(daemonize=True)
                self.assertFalse(stderr.write.called)
                self.assertFalse(exit_.called)
                d.daemonize.assert_called_once_with()
                d.run.assert_called_once_with()


@patch('os.chdir')
@patch('os.chmod')
@patch('os.dup2')
@patch('os.fork')
@patch('os.getpid')
@patch('os.setsid')
@patch('os.umask')
@patch('sys.exit')
@patch('sys.stderr')
@patch('sys.stdin')
@patch('sys.stdout')
@patch('atexit.register')
class DaemonDaemonizeTests(TestCase):

    pidfile = '/tmp/test_rattail_daemon.pid'

    def tearDown(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def fake_open(self, *args):
        # Return mock values for stdin etc.
        if args[0] in ('/tmp/stdin', '/tmp/stdout', '/tmp/stderr'):
            return DEFAULT
        # Real value is returned for PID file.
        return open(*args)

    def test_first_fork_failure(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):
        fork.side_effect = OSError(errno.EIO, "I/O error")
        exit_.side_effect = RuntimeError
        d = daemon.Daemon(self.pidfile)
        self.assertRaises(RuntimeError, d.daemonize)
        stderr.write.assert_called_once_with("fork #1 failed: 5 (I/O error)\n")
        exit_.assert_called_once_with(1)

    def test_first_fork_success(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):
        fork.return_value = 42
        exit_.side_effect = RuntimeError
        d = daemon.Daemon(self.pidfile)
        self.assertRaises(RuntimeError, d.daemonize)
        self.assertFalse(stderr.write.called)
        exit_.assert_called_once_with(0)

    def test_second_fork_failure(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):
        fork.side_effect = [0, OSError(errno.EIO, "I/O error")]
        exit_.side_effect = RuntimeError
        d = daemon.Daemon(self.pidfile)
        self.assertRaises(RuntimeError, d.daemonize)
        stderr.write.assert_called_once_with("fork #2 failed: 5 (I/O error)\n")
        exit_.assert_called_once_with(1)

    def test_second_fork_success_parent(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):
        fork.side_effect = [0, 42]
        exit_.side_effect = RuntimeError
        d = daemon.Daemon(self.pidfile)
        self.assertRaises(RuntimeError, d.daemonize)
        self.assertFalse(stderr.write.called)
        exit_.assert_called_once_with(0)

    def test_second_fork_success_child(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):

        with patch('rattail.daemon.open', new=mock_open(), create=True) as open_:

            fork.side_effect = [0, 0]
            open_.side_effect = self.fake_open
            getpid.return_value = 42

            d = daemon.Daemon(self.pidfile,
                              stdin='/tmp/stdin',
                              stdout='/tmp/stdout',
                              stderr='/tmp/stderr')
            d.daemonize()

            stdout.flush.assert_called_once_with()
            stderr.flush.assert_called_once_with()

            self.assertEqual(open_.call_args_list, [
                    call('/tmp/stdin', 'r'),
                    call('/tmp/stdout', 'a+'),
                    call('/tmp/stderr', 'a+', 0),
                    call(self.pidfile, 'w+'),
                    ])

            stdin.fileno.assert_called_once_with()
            stdout.fileno.assert_called_once_with()
            stderr.fileno.assert_called_once_with()
            self.assertEqual(open_.return_value.fileno.call_count, 3)
            self.assertEqual(dup2.call_args_list, [
                    call(open_.return_value.fileno.return_value, stdin.fileno.return_value),
                    call(open_.return_value.fileno.return_value, stdout.fileno.return_value),
                    call(open_.return_value.fileno.return_value, stderr.fileno.return_value),
                    ])

            register.assert_called_once_with(d.delpid)
            getpid.assert_called_once_with()
            chmod.assert_called_once_with('/tmp/test_rattail_daemon.pid',
                                          stat.S_IRUSR | stat.S_IWUSR)

            with open(self.pidfile) as f:
                pid = f.read()
            self.assertEqual(pid, '42\n')

    def test_pidfile_error(self, register, stdout, stdin, stderr, exit_, umask, setsid, getpid, fork, dup2, chmod, chdir):

        tempdir = tempfile.mkdtemp()
        os.rmdir(tempdir)
        self.pidfile = os.path.join(tempdir, 'test_rattail_daemon.pid')
        self.assertFalse(os.path.exists(tempdir))
        self.assertFalse(os.path.exists(self.pidfile))

        with patch('rattail.daemon.open', new=mock_open(), create=True) as open_:
            fork.side_effect = [0, 0]
            open_.side_effect = self.fake_open

            d = daemon.Daemon(self.pidfile,
                              stdin='/tmp/stdin',
                              stdout='/tmp/stdout',
                              stderr='/tmp/stderr')
            self.assertRaises(IOError, d.daemonize)
            open_.assert_called_with(self.pidfile, 'w+')
            self.assertFalse(chmod.called)
