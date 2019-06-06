#!/usr/bin/env python3

from setuptools import setup

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""

"""Generate a resource file template from a Table Schema JSON file."""

setup(
    name='table-schema-resource-template',
    version='0.1.0',

    author='Christophe Benz',
    author_email='christophe.benz@jailbreak.paris',
    classifiers=[classifier for classifier in classifiers.split('\n') if classifier],
    description=__doc__,

    packages=['table_schema_resource_template'],
    install_requires=[
        'tableschema >= 1.5.1',
        'xlsxwriter >= 1.1.8'
    ],

    entry_points={
        'console_scripts': [
            'table-schema-resource-template = table_schema_resource_template.cli:main',
        ],
    },
)
