# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from os import path
from shutil import rmtree
import sys

from setuptools import setup


NAME = 'mezzanine-sync-pages'
VERSION = '1.0.1'

here = path.abspath(path. dirname(__file__))
with open(path.join(here, 'README.md'), 'rb') as f:
    LONG_DESCRIPTION = f.read().decode('utf-8')


if 'bdist_wheel' in sys.argv:
    for directory in ('build', 'dist', 'mezzanine-sync-pages.egg-info'):
        rmtree(directory, ignore_errors=True)  # cleanup


setup(
    name=NAME,
    packages=['mezzanine_sync_pages'],
    version=VERSION,
    description='Django app to synchronize Mezzanine page content to and from files',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license='MIT',
    author='Enrico Tröger',
    author_email='enrico.troeger@uvena.de',
    url='https://github.com/eht16/mezzanine-sync-pages/',
    project_urls={
        'Travis CI': 'https://travis-ci.org/eht16/mezzanine-sync-pages/',
        'Source code': 'https://github.com/eht16/mezzanine-sync-pages/',
    },
    keywords='django mezzanine pages synchronize',
    python_requires='>=3.5',
    setup_requires=['flake8', 'isort'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
