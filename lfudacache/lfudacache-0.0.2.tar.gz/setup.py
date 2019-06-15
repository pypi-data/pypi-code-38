# -*- coding: utf-8 -*-
"""
lfudacache
==========

License
-------
MIT (see LICENSE file).
"""

import sys
import os.path

from setuptools import setup

sys.path.insert(0, os.path.abspath('lfudacache'))
import __meta__ as meta  # noqa
sys.path.pop(0)

with open('README.md') as f:
    meta_doc = f.read()

setup(
    name=meta.app,
    version=meta.version,
    url=meta.url,
    license=meta.license,
    author=meta.author_name,
    author_email=meta.author_mail,
    description=meta.description,
    long_description=meta_doc,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        ],
    keywords=['cache', 'memoize'],
    packages=['lfudacache'],
    test_suite='lfudacache.tests',
    zip_safe=True,
    platforms='any')
