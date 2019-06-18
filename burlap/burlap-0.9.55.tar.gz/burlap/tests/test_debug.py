from __future__ import print_function
import os

from burlap import common
from burlap.tests.base import TestCase

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

class DebugTests(TestCase):

    def setUp(self):
        super(DebugTests, self).setUp()

        common.set_verbose(True)
        # Ensure we're in burlap's root directory.
        os.chdir(os.path.abspath(os.path.join(CURRENT_DIR, '../..')))
        self._tmp_host_string = common.env.host_string
        self._tmp_is_local = common.env.is_local
        common.env.host_string = 'localhost'
        common.env.is_local = True

    def tearDown(self):
        common.env.host_string = self._tmp_host_string
        common.env.is_local = self._tmp_is_local

    def test_shell(self):
        from burlap.debug import debug
        from burlap import shell

        debug.verbose = True
        assert debug.genv.is_local
        ret = debug.shell(command="echo 'hello1'")
        print('ret:', ret)

        debug.genv.is_local = False
        ret = debug.shell(command="echo 'hello2'")
        print('ret:', ret)

        ret = shell(command="echo 'hello3'")
        print('ret:', ret)
