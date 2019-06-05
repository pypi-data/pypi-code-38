#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('requirements.txt', 'r') as r:
    requirements = r.read().splitlines()

with open('README.md', 'r') as r:
    readme = r.read()

setup(
    name='ambiverseclient',
    version='0.2',
    author="Linus Kohl",
    author_email="linus@munichresearch.com",
    packages=['ambiverseclient'],
    python_requires='>=3.6',
    license='GPLv3',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    url="https://github.com/linuskohl/ambiverse-client"
)
