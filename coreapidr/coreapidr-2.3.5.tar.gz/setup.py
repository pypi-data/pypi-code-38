#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import shutil
import sys


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


version = get_version('coreapidr')


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()


setup(
    name='coreapidr',
    version=version,
    url='https://github.com/drobson1005/python-client',
    license='BSD',
    description='Python client library for Core API.',
    author='Dan Robson',
    author_email='dan@coreapidr.robsoncloud.com',
    packages=get_packages('coreapidr'),
    package_data=get_package_data('coreapidr'),
    install_requires=[
        'coreschema',
        'requests',
        'itypes',
        'uritemplate'
    ],
    entry_points={
        'coreapidr.codecs': [
            'corejson=coreapidr.codecs:CoreJSONCodec',
            'json=coreapidr.codecs:JSONCodec',
            'text=coreapidr.codecs:TextCodec',
            'download=coreapidr.codecs:DownloadCodec',
        ],
        'coreapidr.transports': [
            'http=coreapidr.transports:HTTPTransport',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
