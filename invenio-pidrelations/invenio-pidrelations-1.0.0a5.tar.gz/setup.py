# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds PID relations to the Invenio-PIDStore module."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pydocstyle>=1.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0,!=3.3.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0',
    ],
    'records': [
        'invenio-deposit>=1.0.0a7',
        'invenio-records>=1.0.0b1',
        # FIXME: Added because requirements-builder does not search
        # recursively lowest dependencies.
        'invenio-records-ui>=1.0.0a8',
        'invenio-records-rest>=1.0.0a17',
        'invenio-accounts>=1.0.0b7',
        'Flask-WTF>=0.13.1',
        # Needed in order to have correct alembic upgrade.
        'invenio-oauth2server>=1.0.0b4',
        'invenio-records-files>=1.0.0a9',
        'invenio-files-rest>=1.0.0a15',
    ],
    'indexer': [
        'invenio-indexer>=1.0.0a9',
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask-BabelEx>=0.9.3',
    'flask-oauthlib>=0.9.4',
    'invenio-pidstore>=1.0.0',
    'invenio-rest[cors]>=1.0.0',
    'SQLAlchemy>=1.0.9',
    'marshmallow>=2.15.2',
    'requests-oauthlib>=1.1.0,<1.2.0',
    'oauthlib<3.0.0,>=2.1.0',
    'six>=1.11',
    'urllib3<1.25,>=1.21.1',
    'idna<2.8,>=2.5',
    'SQLAlchemy-Continuum>=1.3,<1.3.5',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_pidrelations', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-pidrelations',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio pidstore persistent identifier relations',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-pidrelations',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_pidrelations = invenio_pidrelations:InvenioPIDRelations',
        ],
        'invenio_base.api_apps': [
            'invenio_pidrelations = invenio_pidrelations:InvenioPIDRelations',
        ],
        'invenio_db.alembic': [
            'invenio_pidrelations = invenio_pidrelations:alembic',
        ],
        'invenio_db.models': [
            'invenio_pidrelations = invenio_pidrelations.models',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_pidrelations',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
