# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Fixtures used by the test suite
# :Created:   lun 22 feb 2016 14:18:21 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019 Lele Gaifax
#

from io import open
from locale import getpreferredencoding
from os import close, getenv, unlink
from os.path import join
import shutil
import subprocess
import tempfile
import unittest


USER_ENCODING = getpreferredencoding() or "UTF-8"

DEFAULT_SPHINX_CONF = """\
extensions = ['metapensiero.sphinx.patchdb']
patchdb_storage = 'patchdb-test.json'
source_suffix = '.txt'
master_doc = 'index'
"""

DEFAULT_INDEX_TXT = """\
PatchDB tests
=============

Contents:

.. toctree::
   :maxdepth: 2

   test
"""


class PatchDBSphinx(object):
    SPHINX_BUILD = 'sphinx-build'
    SPHINX_BUILD_OPTS = ('-b', 'html', '-q', '-d', '_build/doctrees', '.', '_build/html')

    PATCHDB = 'patchdb'
    PATCHDB_SHELVE = 'patchdb-test.json'

    PDBSTATES = 'patchdb-states'

    def __init__(self, db_opts):
        self.db_opts = db_opts
        self.directory = tempfile.mkdtemp()

    def remove(self):
        if not getenv('PATCHDB_TEST_DRD'):
            shutil.rmtree(self.directory)

    def build(self, contents):
        from textwrap import dedent

        for filename, content in contents.items():
            with open(join(self.directory, filename), 'w', encoding='utf-8') as f:
                f.write(dedent(content))

        cmd = [self.SPHINX_BUILD]
        cmd.extend(self.SPHINX_BUILD_OPTS)
        try:
            output = subprocess.check_output(cmd, cwd=self.directory, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.build_error = e.output.decode(USER_ENCODING)
        else:
            output = output.decode(USER_ENCODING)
            warnings = []
            errors = []
            for line in output.splitlines():
                if line.startswith('WARNING:'):
                    warnings.append(line)
                else:
                    errors.append(line)
            self.build_warning = '\n'.join(warnings) if warnings else None
            self.build_error = '\n'.join(errors) if errors else None
        return self.build_error

    def patchdb(self, *more_args, **kwargs):
        cmd = [self.PATCHDB]
        cmd.extend(self.db_opts)
        cmd.extend(more_args)
        cmd.append(self.PATCHDB_SHELVE)
        stderr_fileno, stderr_filename = tempfile.mkstemp()
        try:
            try:
                output = subprocess.check_output(cmd, cwd=self.directory, stderr=stderr_fileno)
                output = output.decode(USER_ENCODING)
            except subprocess.CalledProcessError as e:
                close(stderr_fileno)
                with open(stderr_filename, 'r', encoding=USER_ENCODING) as fe:
                    output = fe.read()
                if e.output:
                    if isinstance(e.output, bytes):
                        output += '\n\n' + e.output.decode(USER_ENCODING)
                    else:
                        output += '\n\n' + e.output
                self.patchdb_output = output
            else:
                close(stderr_fileno)
                with open(stderr_filename, 'r', encoding=USER_ENCODING) as fe:
                    self.patchdb_output = fe.read() + '\n\n' + output
        finally:
            unlink(stderr_filename)

        return output

    def pdbstates(self, subcmd, *more_args):
        cmd = [self.PDBSTATES, subcmd]
        if subcmd == 'restore':
            cmd.extend(self.db_opts)
        cmd.extend(more_args)
        stderr_fileno, stderr_filename = tempfile.mkstemp()
        try:
            try:
                output = subprocess.check_output(cmd, cwd=self.directory, stderr=stderr_fileno)
                output = output.decode(USER_ENCODING)
            except subprocess.CalledProcessError:
                close(stderr_fileno)
                with open(stderr_filename, 'r', encoding=USER_ENCODING) as fe:
                    output = fe.read()
            else:
                close(stderr_fileno)
                with open(stderr_filename, 'r', encoding=USER_ENCODING) as fe:
                    output = fe.read() + '\n\n' + output
        finally:
            unlink(stderr_filename)

        return output


class BaseTestCase(unittest.TestCase):
    DB_OPTION = '--sqlite'
    "The option passed to ``patchdb`` to select the database engine"

    DB_NAME = 'patchdb-test.sqlite'
    "The name of the database to operate on"

    DB_OTHER_OPTIONS = ()

    SPHINX_CONF = DEFAULT_SPHINX_CONF
    "The configuration for the Sphinx environment"

    INDEX_TXT = DEFAULT_INDEX_TXT
    "The entry point of the documentation"

    OTHER_FILES = ()
    "A possible sequence of ``(filename, content)`` tuples"

    NUM_OF_SCRIPTS = 1
    "The number of scripts we expect to be applied"

    @classmethod
    def contents(cls):
        yield 'conf.py', cls.SPHINX_CONF
        yield 'index.txt', cls.INDEX_TXT
        test_txt = getattr(cls, 'TEST_TXT', None)
        if test_txt is not None:
            yield 'test.txt', test_txt
        for fname, content in cls.OTHER_FILES:
            yield fname, content

    @classmethod
    def setUpClass(cls):
        cls.drop_database_if_exists()
        cls.create_database()
        cls.sphinx = PatchDBSphinx((cls.DB_OPTION, cls.DB_NAME) + cls.DB_OTHER_OPTIONS)
        cls.sphinx.build({filename: content for filename, content in cls.contents()})

    @classmethod
    def tearDownClass(cls):
        cls.sphinx.remove()

    @classmethod
    def drop_database_if_exists(cls):
        pass

    @classmethod
    def create_database(cls):
        pass

    @property
    def build_error(self):
        return self.sphinx.build_error

    @property
    def build_warning(self):
        return self.sphinx.build_warning

    @property
    def patchdb_output(self):
        return self.sphinx.patchdb_output

    def setUp(self):
        self.assertIsNone(self.build_error)

    def build(self, contents):
        return self.sphinx.build(contents)

    def patchdb(self, *args, **kwargs):
        return self.sphinx.patchdb(*args, **kwargs)

    def pdbstates(self, *args, **kwargs):
        return self.sphinx.pdbstates(*args, **kwargs)

    def get_connection_and_base_exception(self):
        if self.DB_OPTION == '--sqlite':
            from sqlite3 import connect, OperationalError
            dbpath = join(self.sphinx.directory, self.DB_NAME)
            return connect(dbpath), OperationalError
        elif self.DB_OPTION == '--postgresql':
            from psycopg2 import connect, ProgrammingError
            return connect(self.DB_NAME), ProgrammingError
        elif self.DB_OPTION == '--mysql':
            from pymysql import connect, DatabaseError
            return connect(db=self.DB_NAME), DatabaseError
        elif self.DB_OPTION == '--firebird':
            from fdb import connect, DatabaseError
            return connect(dsn=self.DB_NAME, user=self.USER,
                           password=self.PASSWORD), DatabaseError
        else:
            raise NotImplementedError('Unable to connect with %s' % self.DB_OPTION)

    def test(self):
        output = self.patchdb()
        self.assertIn('Done, applied %d script' % self.NUM_OF_SCRIPTS, output)
        output = self.patchdb()
        self.assertIn('Done, applied 0 scripts', output)
