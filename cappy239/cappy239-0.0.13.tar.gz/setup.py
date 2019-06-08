#!/usr/bin/env python
# https://github.com/AdrianoPereira/cap239/tree/master/cappy239
import os
import re
import sys

from codecs import open
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

if sys.argv[-1] == 'uninstall':
    os.system('rm -rf build')
    os.system('rm -rf dist')
    os.system('rm -rf cappy239.egg-info')

    os.system('twine upload dist/*')
    sys.exit()

# packages = ['cappy239']

requires = [
    'numpy>=1.15.2',
    'matplotlib>=3.1.0'
]

about = {}
with open(os.path.join(here, 'cappy239', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()
# with open('HISTORY.md', 'r', 'utf-8') as f:
#     history = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['cappy239'],
    package_data={'': ['LICENSE', 'NOTICE'], 'requests': ['*.pem']},
    # package_dir={'cappy239': 'cappy239'},
    # include_package_data=True,
    python_requires="!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=requires,
    license=about['__license__'],
)
