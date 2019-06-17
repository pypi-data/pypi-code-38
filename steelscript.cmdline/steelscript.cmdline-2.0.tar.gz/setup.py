# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


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
    name='steelscript.cmdline',
    namespace_packages=['steelscript'],
    version=get_version(),
    author='Riverbed Technology',
    author_email='eng-github@riverbed.com',
    url='http://pythonhosted.org/steelscript',
    license='MIT',
    description='SteelScript support for command-line interaction',
    long_description="""SteelScript for Command-Line Access
===================================

This package contains modules for interacting with a command line or shell.
It contains modules for interacting with different transport types, such as
telnet and ssh, and also contains modules for common parsing of command line
responses.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/

For installation on Windows, this package depends on `pycrypto`,
see more information about installing this pre-requisite here:

https://support.riverbed.com/apis/steelscript/install/steelhead.html#pycrypto
    """,

    platforms='Linux, Mac OS, Windows',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Networking',
    ],

    packages=find_packages(exclude=('gitpy_versioning',)),
    include_package_data=True,

    data_files=(
        ('share/doc/steelscript/docs/cmdline', glob('docs/*.rst')),
        ('share/doc/steelscript/examples/cmdline', glob('examples/*')),
    ),

    install_requires=['paramiko',
                      'scp',
                      'steelscript>=2.0',
                      'ipaddress'],
    extras_require={'test': test,
                    'doc': doc,
                    'dev': [p for p in itertools.chain(test, doc)],
                    'all': ['libvirt']
                    },
    tests_require=test,
    cmdclass={'test': PyTest},
)
