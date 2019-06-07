#!/usr/bin/env python

import os
from setuptools import setup

PACKAGE = 'ems_r25'

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# The VERSION file is created by travis-ci, based on the tag name
version_path = os.path.join(PACKAGE, 'VERSION')
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='Django-EMS-R25',
    version=VERSION,
    packages=[PACKAGE],
    include_package_data=True,
    install_requires=[
        'AuthZ-Group',
        'Django>=1.11.19,<2.0',
        'Django-SupportTools<3.0 ; python_version < "3.0"',
        'Django-SupportTools ; python_version >= "3.0"',
        'lxml',
        'python-dateutil',
        'UW-EMS-Client>=0.11',
        'UW-RestClients-GWS<2.0 ; python_version < "3.0"',
        'UW-RestClients-GWS ; python_version >= "3.0"',
        'UW-RestClients-R25',
    ],
    tests_require=[
        'pycodestyle',
    ],
    license='Apache License, Version 2.0',
    description='Django app generate R25 events from EMS',
    long_description=README,
    url='https://github.com/uw-it-cte/django-ems-r25',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
