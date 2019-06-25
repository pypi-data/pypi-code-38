from yo_extensions import *
from yo_extensions.misc import *
from unittest import TestCase
import os


def path(*args):
    folder = find_root_folder('yo.root')
    return os.path.join(folder, 'tests', 'extensions', *args)