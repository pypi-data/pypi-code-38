#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, 'csgo/__init__.py'), encoding='utf-8') as f:
    __version__ = f.readline().split('"')[1]

install_requires = [
    'steam>=0.8.15,<1.0.0',
    'gevent-eventemitter>=2.0',
    'gevent>=1.1',
    'protobuf>=3.0.0',
    'six>=1.10',
]

if sys.version_info < (3, 4):
    install_requires.append('enum34>=1.0.4')

setup(
    name='csgo',
    version=__version__,
    description='Module for interacting CSGO\'s Game Coordinator',
    long_description=long_description,
    url='https://github.com/ValvePython/csgo',
    author="Rossen Georgiev",
    author_email='rossen@rgp.io',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='valve steam steamid api webapi csgo global offensive',
    packages=['csgo'] + ['csgo.'+x for x in find_packages(where='csgo')],
    install_requires=install_requires,
    zip_safe=True,
)
