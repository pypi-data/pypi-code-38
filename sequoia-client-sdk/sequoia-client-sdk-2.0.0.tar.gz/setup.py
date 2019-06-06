# -*- coding: utf-8 -*-
import os
import re
import sys

import sequoia
from setuptools import setup

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] == 2:
    from codecs import open


def parse_requirements(requirements_file):
    with open(requirements_file) as f:
        return [l.strip().split(';')[0] for l in f if re.match(r'[a-zA-Z].*', l.strip())]


def read_file(file):
    with open(os.path.join(BASE_DIR, file), encoding='utf-8') as f:
        return f.read()


# Read requirements
_requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
_REQUIRES = parse_requirements(_requirements_file)

# Read description
_LONG_DESCRIPTION = read_file('README.rst') + '\n\n' + read_file('HISTORY.rst')

_CLASSIFIERS = (
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
)

_KEYWORDS = ' '.join([
    'python',
])

setup(
    name='sequoia-client-sdk',
    version='2.0.0',
    description=sequoia.__description__,
    long_description=_LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    license='Apache',
    author=sequoia.__author__,
    maintainer=sequoia.__author__,
    url=sequoia.__url__,
    download_url=sequoia.__url__,
    packages=[
        'sequoia',
    ],
    include_package_data=True,
    install_requires=_REQUIRES,
    zip_safe=False,
    keywords=_KEYWORDS,
    classifiers=_CLASSIFIERS,
)
