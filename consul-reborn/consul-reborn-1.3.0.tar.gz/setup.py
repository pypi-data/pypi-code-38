#!/usr/bin/env python3
"""Setup of consul."""

import sys
import re

from setuptools.command.test import test as TestCommand
from setuptools.command.install import install
from setuptools import setup, find_packages


def get_variable_from_file(ffile, variable):
    """Get variable from file."""
    variable_re = "^{} = ['\"]([^'\"]*)['\"]".format(variable)
    with open(ffile, "r") as ffile_obj:
        match = re.search(variable_re, ffile_obj.read(), re.M)
    if match:
        return match.group(1)
    return None


def get_version():
    """Get package version."""
    return get_variable_from_file("consul/__init__.py", "__version__")


def get_requirements(rfile):
    """Get list of required Python packages."""
    requires = list()
    with open(rfile, "r") as reqfile:
        for line in reqfile.readlines():
            requires.append(line.strip())
    return requires


class Install(install):
    """Install class."""
    def run(self):
        # Issue #123: skip installation of consul.aio if python version < 3.4.2
        # as this version or later is required by aiohttp
        if sys.version_info < (3, 4, 2):
            if 'consul/aio' in self.distribution.py_modules:
                self.distribution.py_modules.remove('consul/aio')
        install.run(self)


class PyTest(TestCommand):
    """Class for tests."""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='consul-reborn',
    license='MIT',
    version=get_version(),
    description="Fork of Python client for Consul (http://www.consul.io/) "
    "with some community and mine patches.",
    long_description_content_type='text/markdown',
    long_description="**It's a fork of another fork** "
    "<https://github.com/nzlosh/python-consul>.\n\n" +
    "**The very first origin is** " +
    "<https://github.com/cablehead/python-consul>.\n\n" +
    open('README.md', 'r').read() +
    '\n\n' +
    open('CHANGELOG.md', 'r').read(),
    url='https://github.com/nixargh/python-consul',
    author='nixargh',
    author_email='nixargh@protonmail.com',
    test_suite='tests',
    packages=find_packages(exclude=["tests"]),
    install_requires=get_requirements("./requirements.txt"),
    extras_require={
        'tornado': ['tornado'],
        'asyncio': ['aiohttp'],
        'twisted': ['twisted', 'treq'],
    },
    tests_require=['pytest', 'pytest-twisted'],
    cmdclass={'test': PyTest,
              'install': Install},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration'
    ])
