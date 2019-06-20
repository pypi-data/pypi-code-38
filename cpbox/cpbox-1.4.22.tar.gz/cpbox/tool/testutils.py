import sys
import shutil
import os

from os import path

from cpbox.tool import file
from cpbox.tool import strings

class RandomDir(object):

    def setUp(self):
        self.tests_root_dir = self.get_root_dir()
        name = strings.random_str(10)
        self.temp_dir = path.join(self.tests_root_dir, 'tmp/tmp-%s' % (name))
        file.ensure_dir(self.temp_dir)

    def get_root_dir(self):
        import __main__ as main
        self.is_interactive = hasattr(main, '__file__')
        if self.is_interactive:
            root_dir = path.dirname(path.realpath(sys.argv[0]))
            return root_dir
        else:
            root_dir = os.getcwd()
            return root_dir

    def random_str(self, count=10):
        return strings.random_str(count)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        pass
