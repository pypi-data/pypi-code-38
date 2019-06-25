from yo_extensions import *
from yo_extensions.plots import *
from unittest import TestCase
from yo_extensions.misc import *

def path(*args):
    folder = find_root_folder('yo.root')
    return os.path.abspath(os.path.join(folder, 'tests', 'extensions', 'test_plots_extensions', *args))