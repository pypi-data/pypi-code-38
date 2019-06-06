#!/usr/bin/env python3


"""Generate a resource file template from a Table Schema JSON file."""


import io
import os

from setuptools import setup


# Helpers
def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""

README = read('README.md')


setup(
    name='table-schema-resource-template',
    version='0.1.1',

    author='Christophe Benz',
    author_email='christophe.benz@jailbreak.paris',
    classifiers=[classifier for classifier in classifiers.split('\n') if classifier],
    description=__doc__,
    long_description=README,
    long_description_content_type="text/markdown",

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
