#!/usr/bin/env python

from codecs import open
import os
import setuptools
import sys


here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'beautifulsoup4',
    'click',
    'lxml',
    'pandas',
    'requests',
]

# test_requirements = []

about = {}
with open(os.path.join(here, 'street', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setuptools.setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=setuptools.find_packages(),
    # package_data={},
    # package_dir={},
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=requires,
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'street = street.cli:cli',
        ],
    },
    # cmdclass={},
    # tests_require=test_requirements,
    # extra_require={},
)
