#! /usr/bin/env python3

# dbnomics-data-model -- Define, validate and transform DBnomics data.
# By: Emmanuel Raviart <emmanuel.raviart@cepremap.org>
#
# Copyright (C) 2017-2018 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-data-model
#
# dbnomics-data-model is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-data-model is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Define and validate DBnomics data model."""


from setuptools import find_packages, setup

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Scientific/Engineering
"""

doc_lines = __doc__.split('\n')


setup(
    name='dbnomics-data-model',
    version='0.13.1',

    author='DBnomics Team',
    author_email='contact@nomics.world',
    classifiers=[classifier for classifier in classifiers.split('\n') if classifier],
    description=doc_lines[0],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],

    install_requires=[
        'backports-datetime-fromisoformat',
        'dulwich',
        'jsonschema >= 2.6',
        'python-dateutil',
        'toolz >= 0.8.2',
        'ujson',
    ],
    keywords='data model validation json schema provider dataset time series',
    license='https://www.gnu.org/licenses/agpl-3.0.en.html',
    long_description='\n'.join(doc_lines[2:]),
    url='https://git.nomics.world/dbnomics/dbnomics-data-model',

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'dbnomics-validate = dbnomics_data_model.validate_storage:main',
        ],
    },
)
