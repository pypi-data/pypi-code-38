#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'build_dist':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://configkeeper.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='configkeeper',
    version='0.1.0',
    description='Backup local config files to repo',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Magnus "Loxosceles" Henkel',
    author_email='loxosceles@gmx.de',
    url='https://gitlab.com/loxosceles/configkeeper',
    packages=[
        'configkeeper',
    ],
    package_dir={'configkeeper': 'configkeeper'},
    include_package_data=True,
    install_requires=[
    ],
    license='GNU GPL v3.0',
    zip_safe=False,
    keywords='configkeeper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
