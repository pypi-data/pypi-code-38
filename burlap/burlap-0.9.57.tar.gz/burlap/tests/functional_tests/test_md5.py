from __future__ import with_statement

import hashlib

from fabric.api import hide, run, settings

import burlap
from burlap.tests.functional_tests.base import TestCase

class Md5Tests(TestCase):

    def test_md5sum_empty_file(self):
        try:
            run('touch f1')
            expected_hash = hashlib.md5(''.encode('utf-8')).hexdigest()
            assert burlap.files.file.md5sum('f1') == expected_hash
        finally:
            run('rm -f f1')

    def test_md5sum(self):
        try:
            run('echo -n hello > f2')
            expected_hash = hashlib.md5('hello'.encode('utf-8')).hexdigest()
            assert burlap.files.file.md5sum('f2') == expected_hash
        finally:
            run('rm -f f2')

    def test_md5sum_not_existing_file(self):
        with settings(hide('warnings')):
            assert burlap.files.file.md5sum('doesnotexist') is None
