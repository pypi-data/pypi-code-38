#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the archive interface with hpss."""
import sys
from os.path import isfile
from os import path
# pylint: disable=no-name-in-module
# pylint: disable=import-error
from setuptools.extension import Extension
# pylint: enable=import-error
# pylint: enable=no-name-in-module
from setuptools import setup, find_packages
try:  # pip version 9
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt', session='hack')

HPSS = Extension(
    'pacifica.archiveinterface.backends.hpss._hpssExtensions',
    sources=[
        'pacifica/archiveinterface/backends/hpss/hpssExtensions.c'
    ],
    include_dirs=['/opt/hpss/include'],
    library_dirs=['/opt/hpss/lib'],
    libraries=['tirpc', 'hpsscs', 'hpss'],
    extra_compile_args=['-DLINUX', '-DHPSS51', '-DLITTLEEND']
)

EXT_MODULES = []
if '--with-hpss' in sys.argv:
    EXT_MODULES.append(HPSS)
    sys.argv.remove('--with-hpss')
elif isfile('/opt/hpss/include/hpss_api.h'):
    EXT_MODULES.append(HPSS)
if '--without-hpss' in sys.argv:
    EXT_MODULES = []
    sys.argv.remove('--without-hpss')

setup(
    name='pacifica-archiveinterface',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Archive Interface',
    url='https://github.com/pacifica/pacifica-archiveinterface/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='david.brown@pnnl.gov',
    packages=find_packages(),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-archiveinterface=pacifica.archiveinterface.__main__:main',
            'pacifica-archiveinterface-cmd=pacifica.archiveinterface.__main__:cmd'
        ],
    },
    install_requires=[str(ir.req) for ir in INSTALL_REQS],
    ext_modules=EXT_MODULES
)
