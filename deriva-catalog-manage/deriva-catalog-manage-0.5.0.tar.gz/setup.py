#
# Copyright 2018 University of Southern California
# Distributed under the Apache License, Version 2.0. See LICENSE for more info.
#

""" Installation script for the deriva-catalog-manage package.
"""

from setuptools import setup, find_packages
import re
import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('deriva/utils/catalog/version.py', encoding='utf_8_sig').read()
    ).group(1)


def get_readme_contents():
    with io.open('README.md') as readme_file:
        return readme_file.read()


url = 'https://github.com/informatics-isi-edu/deriva-catalog-manage'
author = 'USC Information Sciences Institute, Informatics Systems Research Division'
author_email = 'isrd-support@isi.edu'


setup(
    name='deriva-catalog-manage',
    description='DERIVA catalog management utilities built on deriva-py.',
    long_description='For further information, visit the project [homepage](%s).' % url,
    long_description_content_type='text/markdown',
    url=url,
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    version=__version__,
    packages=find_packages(exclude=["tests", "extra_tests", "examples"]),
    package_data={},
    python_requires='>=3.5.4',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'deriva-catalog-dump = deriva.utils.catalog.manage.dump_catalog:main',
            'deriva-catalog-config = deriva.utils.catalog.components.deriva_catalog:main',
            'deriva-csv = deriva.utils.catalog.manage.deriva_csv:main [csv]'
        ],
    },
    requires=[
        'deriva',
        'requests',
        'graphviz',
        'tabulate',
        'yapf'
    ],
    install_requires=[
        'requests',
        'graphviz',
        'tabulate',
        'yapf',
        'deriva>=0.8.4'
    ],
    extras_require={
        'csv': ['goodtables',
                'python-dateutil',
                'jsonschema==2.6.0']
    },
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
