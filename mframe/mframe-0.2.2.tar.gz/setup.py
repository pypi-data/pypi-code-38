#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import find_packages, setup, Command
from shutil import rmtree
import os
import sys


VERSION = '0.2.2'


here = os.path.abspath(os.path.dirname(__file__))



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
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))
        os.system('jython setup.py bdist_egg')

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


setup(
    name='mframe',
    version=VERSION,
    description='A lightweight single file DataFrame implementation that works on older Python distrubtions such as Jython.',
    long_description=open('README.rst').read(),
    author='Jonathan Harrington',
    author_email='jonathan@jonharrington.org',
    url='https://github.com/prio/mframe',
    license='BSD',
    py_modules=['mframe'],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: CPython',
    ],    
    cmdclass={
        'upload': UploadCommand,
    },    
)