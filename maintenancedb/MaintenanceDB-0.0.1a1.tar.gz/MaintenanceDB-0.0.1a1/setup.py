#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for MaintenanceDB.
'''
import uuid
import codecs

from setuptools import setup, find_packages

__author__ = 'Mircea Ulinic <ping@mirceaulinic.net>'

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

with codecs.open('README.rst', 'r', encoding='utf8') as file:
    long_description = file.read()

print(long_description)

setup(
    name='MaintenanceDB',
    version='0.0.1a1',
    packages=find_packages(),
    author='Mircea Ulinic',
    author_email='ping@mirceaulinic.net',
    description='Manage providers maintenance notifications and fire alarms or invoke hooks',
    long_description=long_description,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers'
    ],
    url='https://github.com/mirceaulinic/maintenance',
    license="Apache License 2.0",
    keywords=('networking', 'maintenance', 'webhooks', 'alerts', 'metrics'),
    include_package_data=True,
    install_requires=reqs
)
