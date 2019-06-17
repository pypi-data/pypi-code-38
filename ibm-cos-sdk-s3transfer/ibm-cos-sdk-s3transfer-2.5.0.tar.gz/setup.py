#!/usr/bin/env python
import os
import re
import sys
from setuptools import setup, find_packages

# IbmCos sdk python version check
_valid  =  sys.version_info[:2] == (2, 7) or sys.version_info >= (3,4)
if not _valid:
    sys.exit("Sorry, IBM COS SDK only supports versions 2.7, 3.4, 3.5, 3.6, 3.7 of python.")


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([a-z0-9.]+)['"]''')


requires = [
    'ibm-cos-sdk-core>=2.0.0',
]

if sys.version_info[0] == 2:
    # concurrent.futures is only in python3, so for
    # python2 we need to install the backport.
    requires.append('futures>=2.2.0,<4.0.0')
    requires.append('backports.functools-lru-cache>=1.5')

def get_version():
    init = open(os.path.join(ROOT, 'ibm_s3transfer', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='ibm-cos-sdk-s3transfer',
    version=get_version(),
    description='IBM S3 Transfer Manager',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    author='IBM',
    author_email='',
    url='https://github.com/ibm/ibm-cos-sdk-python-s3transfer',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
)
