#!/usr/bin/env python3


""" Setup script """


import importlib
import os

import setuptools


def _setup():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'CHANGELOG.rst')) as file_:
        changelog = file_.read()

    version = changelog.splitlines()[4]

    # Add the command class for use in this very setup script. Which means the
    # project is probably not installed yet. To achieve this the module
    # containing the class is dynamically imported.
    module_name = 'core'
    module_path = os.path.join(
        here, 'src', 'zapp',
        '{}.py'.format(module_name),
    )
    module_spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    cmdclass = {
        'bdist_zapp': getattr(module, 'bdist_zapp'),
    }

    setuptools.setup(
        # see 'setup.cfg'
        version=version,
        cmdclass=cmdclass,
    )


if __name__ == '__main__':
    _setup()


# EOF
