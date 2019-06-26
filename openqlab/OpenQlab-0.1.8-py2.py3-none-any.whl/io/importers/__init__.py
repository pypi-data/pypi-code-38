import os.path
import glob
import sys
from typing import Dict
import importlib
from . import utils

if __name__ == '__main__':
    importer_dir = os.path.abspath(sys.argv[0])
else:
    importer_dir = os.path.abspath(__file__)

importer_dir = os.path.dirname(importer_dir)

validImporters: Dict = {}

'''
auto importers are used to automatically determine the file _type,
they must raise utils.UnknownFileType if they don't know what to do with
this file.
'''
validAutoImporters: Dict = {}
for fn in glob.glob(importer_dir + "/*.py"):
    importer = utils.get_file_basename(fn)
    if importer == '__init__' or importer == 'utils':
        continue
    try:
        importer = importlib.import_module('.' + importer, package='OpenQlab.io.importers')
    except ImportError as e:
        print(e)
        continue
    try:
        validImporters.update(importer.get_importers())
        validAutoImporters.update(importer.get_auto_importers())
    except AttributeError as e:
        continue
