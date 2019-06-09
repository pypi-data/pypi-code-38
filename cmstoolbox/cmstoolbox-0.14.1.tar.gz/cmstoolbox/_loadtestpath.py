"""
This module is used to add directories listed in various packages'
``test/path.txt`` file to the system path.
If imported from a directory with a file called ``path.txt``,
it will assume that it is inside of a packages ``test`` directory
and modify the system path to add those directories too.
This is done by calling ``add_path('.')`` at the end of this module.
In general, this package should not be used for loading modules.
Its purpose is to temporarily put python scripts into the system's path
so the scripts can be imported for documentation and unit tests.
If your package consists of modules that are regularly imported,
lay out your repository appropriately to live in the ``OpsSpace`` directory.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import sys


def add_path(package):
    """
    Add the directories for a given package to Python's import path.
    The default behavior is to look for ``../<package>/test/path.txt``.
    For each directory listed in that file, ``../<package>/<dir>`` will
    be added to the system path.
    The reason for the leading ``..`` is that the module is designed to be called
    from within the ``OpsSpace/docs`` directory or a package's ``test`` directory.
    Paths are appended to the front of the path, so directories at the bottom
    of the ``test/path.txt`` will be loaded first.

    :param str package: Is the name of the package to load the test path for.
    """

    path_file_name = '../{0}/test/path.txt'.format(package)

    if os.path.exists(path_file_name):
        with open(path_file_name, 'r') as path_file:
            for directory in path_file.readlines():
                sys.path.insert(0, os.path.abspath(
                    '../{0}/{1}'.format(package, directory.strip('\n'))
                    ))


add_path('.')
