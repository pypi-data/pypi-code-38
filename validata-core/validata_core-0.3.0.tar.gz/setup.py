#!/usr/bin/env python3

from setuptools import setup

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: GNU Affero General Public License v3
"""


setup(
    name='validata_core',
    version='0.3.0',

    author='Christophe Benz',
    author_email='christophe.benz@jailbreak.paris',
    classifiers=[classifier for classifier in classifiers.split('\n') if classifier],
    description=__doc__,

    packages=['validata_core'],
    include_package_data=True,
    package_data={
        'validata_core': ['validata_spec.json'],
    },
    install_requires=[
        'goodtables',
        'importlib_resources',
        'requests',
        'tabulator',
        'tableschema',
        'toml',
        'toolz',

        # for custom_checks
        'python-stdnum'
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
    ],

    entry_points={
        'console_scripts': [
            'validata = validata_core.cli:cli',
        ],
    },
)
