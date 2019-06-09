import sys
import os
import inspect

LIB_PATHS = [
    'ptyprocess',
    'pexpect',
    'pyyaml/lib3',
    'jinja',
    'markupsafe/src',
    'yamlreader/src/main/python',
    'six'
]

LIB_BASE_PATH = "../lib"

for lib_path in LIB_PATHS:
    lib_dir = os.path.join(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
        LIB_BASE_PATH,
        lib_path)
    sys.path.insert(0, lib_dir)
