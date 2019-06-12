#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import setuptools
from pathlib import Path

name = 'bout_install'
root_path = Path(__file__).parent
init_path = root_path.joinpath(name, '__init__.py')
readme_path = root_path.joinpath('README.md')

# https://packaging.python.org/guides/single-sourcing-package-version/
with init_path.open('r') as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError('Unable to find version string.')

with readme_path.open('r') as f:
    long_description = f.read()

setuptools.setup(
    name=name,
    version=version,
    author='Michael Løiten',
    author_email='michael.l.magnussen@gmail.com',
    description='Python package to install BOUT++ and its dependencies',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CELMA-project/bout_install',
    packages=setuptools.find_packages(),
    keywords=['bout++', 'bout', 'installation', 'plasma', 'turbulence'],
    install_requires=['requests>=2.20.1'],
    package_data={
        # Include all .ini files
        '': ['*.ini']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v3 or later (LGPLv3+)'),
        'Operating System :: OS Independent',
    ],
    entry_points={'console_scripts': [
        'bout_install = bout_install.main:bout_install_command_line'
    ]},
)
