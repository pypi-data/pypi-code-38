# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from __future__ import print_function, division

import sys
import itertools
from glob import glob

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    raise ImportError(
        'The setuptools package is required to install this library. See '
        '"https://pypi.python.org/pypi/setuptools#installation-instructions" '
        'for further instructions.'
    )

from gitpy_versioning import get_version


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main("%s tests" % " ".join(self.test_args))
        sys.exit(errno)

test = ['pytest', 'testfixtures']
doc = ['sphinx']

setup(
    name='steelscript.steelhead',
    namespace_packages=['steelscript'],
    version=get_version(),
    author='Riverbed Technology',
    author_email='eng-github@riverbed.com',
    url='http://pythonhosted.org/steelscript',
    license='MIT',
    description=('Python modules for interacting with '
                 'Riverbed SteelHead with SteelScript'),
    long_description="""SteelScript for SteelHead
=========================

This package provides device specific bindings for interacting
with Riverbed SteelHead devices as part of the Riverbed Steelscript
for Python.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/
    """,

    platforms='Linux, Mac OS, Windows',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Networking',
    ],

    python_requires='>3.5.0',

    packages=find_packages(exclude=('gitpy_versioning',)),
    include_package_data=True,

    data_files=(
        ('share/doc/steelscript/docs/steelhead', glob('docs/*.rst')),
        ('share/doc/steelscript/examples/steelhead', glob('examples/*')),
    ),

    install_requires=['ipaddress',
                      'netaddr',
                      'steelscript.cmdline>=2.0'],
    extras_require={'test': test,
                    'doc': doc,
                    'dev': [p for p in itertools.chain(test, doc)],
                    'all': []
                    },
    tests_require=test,
    cmdclass={'test': PyTest},
    entry_points={'portal.plugins': [
        'steelhead = steelscript.steelhead.appfwk.plugin:SteelHeadPlugin'
    ]}
)
