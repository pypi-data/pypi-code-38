from yo_extensions.misc import find_root_folder
from yo_extensions import *
import os


def path(*args):
    folder = find_root_folder('yo.root')
    return os.path.join(folder, 'tests', 'ml', *args)