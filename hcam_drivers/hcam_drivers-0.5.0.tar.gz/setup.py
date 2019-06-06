#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import glob
import os
import sys

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'astropy',
    'pyserial',
    'tornado',
    'pyaml',
    'configobj',
    'tqdm',
    'hcam_widgets'
]
if sys.version_info[0] == 2:
    requirements.append('pymodbus')
else:
    requirements.append('pymodbus3')

test_requirements = [
    # TODO: put package test requirements here
]

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']

setup(
    name='hcam_drivers',
    version='0.5.0',
    description="Observation planning and finding charts for HiPerCAM",
    long_description=readme + '\n\n' + history,
    author="Stuart Littlefair",
    author_email='s.littlefair@shef.ac.uk',
    url='https://github.com/HiPERCAM/hcam-drivers',
    download_url='https://github.com/HiPERCAM/hcam-drivers/archive/v0.5.0.tar.gz',
    packages=[
        'hcam_drivers',
        'hcam_drivers.utils',
        'hcam_drivers.hardware'
    ],
    package_dir={'hcam_drivers':
                 'hcam_drivers'},
    include_package_data=True,
    scripts=scripts,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='hcam-drivers',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
