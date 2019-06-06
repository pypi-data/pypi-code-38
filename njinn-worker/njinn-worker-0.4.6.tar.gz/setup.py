#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command


NAME = 'njinn-worker'
DESCRIPTION = 'Njinn Worker'
AUTHOR = 'Njinn Technologies GmbH'
EMAIL = 'contact@njinn.io'
REQUIRES_PYTHON = '>=3.7'
VERSION = '0.4.6'
REQUIRED = [
    "celery >=4.2, <4.3",
    "requests >=2.21, <2.22",
    "requests_jwt >=0.5, <0.6",
    "gitpython >=2.1, <2.2",
    "virtualenv >=16.6, <16.7"
]
EXTRAS = {}


here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=['worker'],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points={
        'console_scripts': ['njinn-worker=worker.__main__:main'],
    },
    include_package_data=True,
    license='Other/Proprietary License',
    classifiers=[
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent'
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)
