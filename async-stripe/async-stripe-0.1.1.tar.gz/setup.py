import setuptools
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

github_url = "https://github.com/cglacet/async-stripe"

#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
doclink = """
## Documentation

The full documentation is at http://async-stripe.rtfd.org."""

setup(
    name='async-stripe',
    version='0.1.1',
    description='An asynchronous wrapper for the Stripe payment API.',
    long_description=readme + '\n\n' + doclink,
    long_description_content_type="text/markdown",
    author='Christian Glacet',
    author_email='cglacet@kune.tech',
    url=github_url,
    project_urls={
        'Bug Reports': f'{github_url}/issues',
        'Source': github_url,
    },
    packages=setuptools.find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "aiohttp-asynctools >= 0.1.2",
        "aiohttp"
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "pytest-asyncio",
        "pytest-subtests",
    ],
    license='MIT',
    zip_safe=False,
    keywords='async-stripe',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)