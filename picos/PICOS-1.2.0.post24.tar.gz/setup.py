#!/usr/bin/python

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C) 2018-2019 Maximilian Stahlberg
#
# This file is part of PICOS Release Scripts.
#
# PICOS Release Scripts are free software: you can redistribute it and/or modify
# them under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS Release Scripts are distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

import os

try:
    from setuptools import setup
    from setuptools.command.sdist import sdist as _sdist
except ImportError:
    from distutils.core import setup
    from distutils.command.sdist import sdist as _sdist
    if hasattr(os, 'link'):  # prevent distutils hardlinking
        del os.link

try:
    from version import get_version, get_base_version
except ImportError:
    # PyPI strips version.py from the source package as it's not part of the installation.
    LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    VERSION_FILE = os.path.join(LOCATION, "picos", ".version")

    def get_base_version():
        with open(VERSION_FILE, "r") as versionFile:
            return versionFile.read().strip()

    get_version = get_base_version


class sdist(_sdist):
    """sdist commande, changing .version to `get_version()` result."""
    def make_release_tree(self, base_dir, files):
        """Call `super().make_relese_tree()` and change .version"""
        _sdist.make_release_tree(self, base_dir, files)
        with open(os.path.join(base_dir, "picos", ".version"), 'w') as file:
            file.write(get_version() + '\n')

setup(
    name = 'PICOS',
    version = get_version(),
    author = 'G. Sagnol, M. Stahlberg',
    author_email = 'incoming+picos-api/picos@incoming.gitlab.com',
    packages = ['picos', 'picos.constraints', 'picos.solvers'],
    package_data = {'picos': ['.version']},
    description = 'A Python interface to conic optimization solvers.',
    long_description = open('README.md', 'rb').read().decode('utf8'),
    long_description_content_type = 'text/markdown',
    install_requires = [
        "CVXOPT >= 1.1.4",
        "numpy  >= 1.6.2"
    ],
    keywords = [
        'conic optimization',
        'convex optimization'
        'linear programming',
        'quadratic programming',
        'second order cone programming',
        'semidefinite programming',
        'exponential cone programming'
    ],
    classifiers = [
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
    ],
    url = 'https://gitlab.com/picos-api/picos',
    download_url = 'https://gitlab.com/picos-api/picos/tags/v{}'.format(get_base_version()),
    cmdclass = {'sdist': sdist}
)
