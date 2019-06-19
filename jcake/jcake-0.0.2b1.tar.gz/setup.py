#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


DESCRIPTION = 'Simplify teamates DEVOPS life'

URL = 'http://git.kanzhun-inc.com/liulong/jcake.git'

EMAIL = 'topgun.chuter@gmail.com'
AUTHOR = "chuter",
VERSION = None


REQUIRED = ['Click>=6.0', 'crayons']  # noqa

TEST_REQUIREMENTS = [
    'pytest-cov',
    'pytest-mock',
    'pytest-xdist',
    'pytest==3.9.2'
]

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, 'src')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count
            self.pytest_args = ['-n', str(cpu_count())]
        except (ImportError, NotImplementedError):
            self.pytest_args = ['-n', '1']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


meta = {}
if VERSION is None:
    with open(os.path.join(src, 'jcake', 'meta.py')) as f:
        exec(f.read(), meta)
else:
    meta['__version__'] = VERSION


setup(
    name=meta['__name__'],
    version=meta['__version__'],
    description=DESCRIPTION,
    license='BSD',
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires=">3.4",
    install_requires=REQUIRED,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'jcake=jcake:cli',
            'java.cake=jcake:cli',
        ],
    },
    keywords=[
        'jcake', 'java', 'develop', 'DEVOPS', 'lifecycle'
    ],
    cmdclass={'test': PyTest},
    tests_require=TEST_REQUIREMENTS,
    setup_requires=['pytest-runner'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
