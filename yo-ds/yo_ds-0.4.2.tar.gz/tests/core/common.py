import unittest
import os
from yo_core import *
from yo_extensions.misc import find_root_folder


class LinqTestBase(unittest.TestCase):

    def assertQuery(self, q, *args):
        self.assertListEqual(
            list(args),
            list(q)
        )

    def path(self, *args):
        folder = find_root_folder('yo.root')
        return os.path.join(folder,'tests','core',*args)



