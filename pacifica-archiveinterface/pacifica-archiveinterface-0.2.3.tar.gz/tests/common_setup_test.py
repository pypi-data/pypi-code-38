#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and tear down the class cleaning up files."""
import stat
from os import remove, chmod, rmdir
from os.path import isdir, isfile, join, sep


class SetupTearDown(object):
    """Clean up temporary files before and after tests."""

    @staticmethod
    def _cleanup():
        """Clean up temporary files in /tmp."""
        file_list = [
            '{}{}'.format(sep, join('tmp', '1234')),
            '{}{}'.format(sep, join('tmp', '1235')),
            '{}{}'.format(sep, join('tmp', 'cptests', '1235')),
            '{}{}'.format(sep, join('tmp', '12345')),
            '{}{}'.format(sep, join('tmp', '5678')),
            '{}{}'.format(sep, join('tmp', '15', 'cd', '5b', '75bcd15')),
            '{}{}'.format(sep, join('tmp', 'a', 'b', 'd'))
        ]
        dir_list = [
            '{}{}'.format(sep, join('tmp', 'cptests')),
            '{}{}'.format(sep, join('tmp', 'a', 'b')),
            '{}{}'.format(sep, join('tmp', 'a')),
            '{}{}'.format(sep, join('tmp', '15', 'cd', '5b')),
            '{}{}'.format(sep, join('tmp', '15', 'cd')),
            '{}{}'.format(sep, join('tmp', '15')),
            '{}{}'.format(sep, join('tmp', '39')),
        ]
        for fname in file_list:
            if isfile(fname):
                chmod(fname, stat.S_IWRITE)
                remove(fname)
        for dname in dir_list:
            if isdir(dname):
                chmod(dname, stat.S_IWRITE)
                rmdir(dname)

    def setup_method(self, *_args, **_kwargs):
        """Call cleanup."""
        self._cleanup()

    def teardown_method(self, *_args, **_kwargs):
        """Call cleanup."""
        self._cleanup()
