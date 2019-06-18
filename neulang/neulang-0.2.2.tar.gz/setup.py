#! /usr/bin/env python

# This file is part of neulang

# neulang - A language sitting on top of Python that executes pseudocode that's very close to natural language.

# @author Andrew Phillips
# @copyright 2017-2019 Andrew Phillips <skeledrew@gmail.com>

# neulang is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.

# neulang is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.

# You should have received a copy of the GNU Affero General Public
# License along with neulang.  If not, see <http://www.gnu.org/licenses/>.

import sys
from os.path import join, dirname

from setuptools import setup

from neulang.main import __meta__, __version__

setup(
    name=__meta__.get('name', 'neulang'),
    version=__version__,
    entry_points={
        'console_scripts': [
            'neu = neulang.main:run',
        ],
    },
    author='Andrew Phillips',
    author_email='skeledrew@gmail.com',
    description='Executable org-formatted pseudocode embedded in Python.',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url='https://gitlab.com/skeledrew/neulang',
    packages=['neulang', 'tests'],
    platforms=['any'],
    install_requires = [
        'docopt',
        'adapt-parser',
    ],
    license='AGPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development',
    ])
